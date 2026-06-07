package main

import (
	"fmt"
	"log"
	"time"

	"github.com/austinyuch/asynq"
)

func main() {
	r := asynq.RedisClientOpt{Addr: "localhost:16382"}
	c := asynq.NewClient(r)
	defer c.Close()
	for i := 0; i < 8; i++ {
		if _, err := c.Enqueue(asynq.NewTask("email:welcome", []byte(fmt.Sprintf(`{"user_id": %d}`, i))), asynq.Queue("default")); err != nil {
			log.Fatal(err)
		}
	}
	for i := 0; i < 5; i++ {
		if _, err := c.Enqueue(asynq.NewTask("report:generate", []byte(fmt.Sprintf(`{"report": %d}`, i))), asynq.Queue("critical"), asynq.ProcessIn(2*time.Hour)); err != nil {
			log.Fatal(err)
		}
	}
	for i := 0; i < 3; i++ {
		if _, err := c.Enqueue(asynq.NewTask("image:resize", []byte(fmt.Sprintf(`{"img": %d}`, i))), asynq.Queue("low"), asynq.MaxRetry(3)); err != nil {
			log.Fatal(err)
		}
	}
	// archive a couple via inspector
	insp := asynq.NewInspector(r)
	defer insp.Close()
	tasks, err := insp.ListPendingTasks("low")
	if err != nil {
		log.Fatal(err)
	}
	for i, t := range tasks {
		if i >= 2 {
			break
		}
		if err := insp.ArchiveTask("low", t.ID); err != nil {
			log.Fatal(err)
		}
	}
	fmt.Println("seeded: 8 pending(default), 5 scheduled(critical), 1 pending + 2 archived(low)")
}
