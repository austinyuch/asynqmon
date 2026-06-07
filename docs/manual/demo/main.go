// Command demo seeds a Valkey/Redis instance with tasks in every state the
// Asynqmon UI can display, then keeps a real worker + scheduler alive so the
// Servers and Schedulers pages show live data while screenshots are taken.
//
// Canonical demo-data source for docs/manual (see docs/MANUAL_GENERATION_GUIDE.md).
// Run against a registry-governed Valkey allocation:
//
//	go run ./docs/manual/demo -redis_addr=localhost:16382
//
// The process stays alive until SIGINT/SIGTERM.
package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/austinyuch/asynq"
)

func main() {
	redisAddr := flag.String("redis_addr", "localhost:16382", "redis/valkey address")
	flag.Parse()
	r := asynq.RedisClientOpt{Addr: *redisAddr}

	client := asynq.NewClient(r)
	defer client.Close()

	must := func(_ *asynq.TaskInfo, err error) {
		if err != nil {
			log.Fatal(err)
		}
	}

	// pending (default queue)
	for i := 0; i < 8; i++ {
		must(client.Enqueue(asynq.NewTask("email:welcome", []byte(fmt.Sprintf(`{"user_id": %d, "template": "welcome-v2"}`, 1000+i))),
			asynq.Queue("default"), asynq.Retention(2*time.Hour)))
	}
	// scheduled (critical queue, +2h)
	for i := 0; i < 5; i++ {
		must(client.Enqueue(asynq.NewTask("report:generate", []byte(fmt.Sprintf(`{"report_id": %d, "format": "pdf"}`, 70+i))),
			asynq.Queue("critical"), asynq.ProcessIn(2*time.Hour)))
	}
	// low queue: a few pending, two to archive
	for i := 0; i < 4; i++ {
		must(client.Enqueue(asynq.NewTask("image:resize", []byte(fmt.Sprintf(`{"image": "banner-%d.png", "width": 1280}`, i))),
			asynq.Queue("low"), asynq.MaxRetry(3)))
	}
	// retry: task that always fails, plenty of retries left
	must(client.Enqueue(asynq.NewTask("sync:export", []byte(`{"dest": "s3://acme-archive/2026-06"}`)),
		asynq.Queue("default"), asynq.MaxRetry(10)))
	// archived: fails with MaxRetry(0) -> straight to archived
	must(client.Enqueue(asynq.NewTask("billing:charge", []byte(`{"invoice": "INV-2026-0607", "amount_cents": 129900}`)),
		asynq.Queue("critical"), asynq.MaxRetry(0)))
	// active: long-running task the worker picks up and holds
	must(client.Enqueue(asynq.NewTask("video:transcode", []byte(`{"video": "keynote-2026.mp4", "profile": "1080p"}`)),
		asynq.Queue("default"), asynq.Timeout(30*time.Minute)))
	// completed fodder
	for i := 0; i < 6; i++ {
		must(client.Enqueue(asynq.NewTask("email:digest", []byte(fmt.Sprintf(`{"user_id": %d}`, 2000+i))),
			asynq.Queue("default"), asynq.Retention(2*time.Hour)))
	}
	// aggregating: grouped tasks with a long grace period so they stay visible
	for i := 0; i < 5; i++ {
		must(client.Enqueue(asynq.NewTask("metrics:event", []byte(fmt.Sprintf(`{"event": "page_view", "n": %d}`, i))),
			asynq.Queue("default"), asynq.Group("metrics-batch")))
	}

	// archive the two image:resize extras via Inspector (real admin API)
	insp := asynq.NewInspector(r)
	defer insp.Close()
	if pend, err := insp.ListPendingTasks("low"); err == nil {
		for i, t := range pend {
			if i >= 2 {
				break
			}
			if err := insp.ArchiveTask("low", t.ID); err != nil {
				log.Fatal(err)
			}
		}
	}

	// real worker: weighted queues; handlers produce completed/retry/archived/active states
	srv := asynq.NewServer(r, asynq.Config{
		Concurrency: 4,
		Queues:      map[string]int{"critical": 6, "default": 3, "low": 1},
		GroupGracePeriod: 10 * time.Minute, // keep metrics:event in aggregating state
		GroupMaxSize:     20,
	})
	mux := asynq.NewServeMux()
	mux.HandleFunc("email:welcome", func(ctx context.Context, t *asynq.Task) error { return nil })
	mux.HandleFunc("email:digest", func(ctx context.Context, t *asynq.Task) error { return nil })
	mux.HandleFunc("image:resize", func(ctx context.Context, t *asynq.Task) error { return nil })
	// scheduler-enqueued types: handled so long-lived demo sessions stay clean
	mux.HandleFunc("report:generate", func(ctx context.Context, t *asynq.Task) error { return nil })
	mux.HandleFunc("cleanup:tmp", func(ctx context.Context, t *asynq.Task) error { return nil })
	mux.HandleFunc("sync:export", func(ctx context.Context, t *asynq.Task) error {
		return errors.New("upstream S3 bucket unreachable (demo: stays in retry)")
	})
	mux.HandleFunc("billing:charge", func(ctx context.Context, t *asynq.Task) error {
		return errors.New("card declined (demo: MaxRetry 0 -> archived)")
	})
	mux.HandleFunc("video:transcode", func(ctx context.Context, t *asynq.Task) error {
		select { // hold the task in active state until shutdown
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(25 * time.Minute):
			return nil
		}
	})
	if err := srv.Start(mux); err != nil {
		log.Fatal(err)
	}

	// real scheduler: entries visible on the Schedulers page
	sched := asynq.NewScheduler(r, &asynq.SchedulerOpts{})
	if _, err := sched.Register("*/5 * * * *", asynq.NewTask("report:generate", []byte(`{"report_id": 99, "format": "csv"}`)), asynq.Queue("critical")); err != nil {
		log.Fatal(err)
	}
	if _, err := sched.Register("@every 1h", asynq.NewTask("cleanup:tmp", []byte(`{"older_than": "24h"}`)), asynq.Queue("low")); err != nil {
		log.Fatal(err)
	}
	if err := sched.Start(); err != nil {
		log.Fatal(err)
	}

	fmt.Println("demo seeded: pending/scheduled/retry/archived/active/completed/aggregating + live worker & scheduler")
	fmt.Println("press Ctrl-C (or SIGTERM) to shut down")

	sig := make(chan os.Signal, 1)
	signal.Notify(sig, syscall.SIGINT, syscall.SIGTERM)
	<-sig
	sched.Shutdown()
	srv.Shutdown()
}
