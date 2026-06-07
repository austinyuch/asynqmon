import React from "react";
import { connect, ConnectedProps } from "react-redux";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { Theme, ThemeProvider, StyledEngineProvider } from "@mui/material/styles";
import { makeStyles } from 'tss-react/mui';
import type { CSSObject } from 'tss-react';
import AppBar from "@mui/material/AppBar";
import Drawer from "@mui/material/Drawer";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Snackbar from "@mui/material/Snackbar";
import SnackbarContent from "@mui/material/SnackbarContent";
import IconButton from "@mui/material/IconButton";
import Slide from "@mui/material/Slide";
import { TransitionProps } from "@mui/material/transitions";
import MenuIcon from "@mui/icons-material/Menu";
import BarChartIcon from "@mui/icons-material/BarChart";
import LayersIcon from "@mui/icons-material/Layers";
import SettingsIcon from "@mui/icons-material/Settings";
import ScheduleIcon from "@mui/icons-material/Schedule";
import FeedbackIcon from "@mui/icons-material/Feedback";
import TimelineIcon from "@mui/icons-material/Timeline";
import DoubleArrowIcon from "@mui/icons-material/DoubleArrow";
import CloseIcon from "@mui/icons-material/Close";
import { AppState } from "./store";
import { paths as getPaths } from "./paths";
import { isDarkTheme, useTheme } from "./theme";
import { closeSnackbar } from "./actions/snackbarActions";
import { toggleDrawer } from "./actions/settingsActions";
import ListItemLink from "./components/ListItemLink";
import SchedulersView from "./views/SchedulersView";
import DashboardView from "./views/DashboardView";
import TasksView from "./views/TasksView";
import TaskDetailsView from "./views/TaskDetailsView";
import SettingsView from "./views/SettingsView";
import ServersView from "./views/ServersView";
import RedisInfoView from "./views/RedisInfoView";
import MetricsView from "./views/MetricsView";
import PageNotFoundView from "./views/PageNotFoundView";
import Logo from "./images/logo-color.svg?react";
import LogoDarkTheme from "./images/logo-white.svg?react";




const drawerWidth = 220;

// App computes its own theme (from settings) before rendering ThemeProvider,
// so the theme is passed to tss-react as a param instead of via context.
const useStyles = makeStyles<{ theme: Theme }>()((_unusedContextTheme, { theme }) => ({
    root: {
      display: "flex",
    },
    toolbar: {
      paddingRight: 24, // keep right padding when drawer closed
    },
    toolbarIcon: {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-end",
      padding: "0 8px",
      ...(theme.mixins.toolbar as CSSObject),
    },
    appBar: {
      backgroundColor: theme.palette.background.paper,
      zIndex: theme.zIndex.drawer + 1,
    },
    menuButton: {
      marginRight: theme.spacing(1),
      color: isDarkTheme(theme)
        ? theme.palette.grey[100]
        : theme.palette.grey[700],
    },
    menuButtonHidden: {
      display: "none",
    },
    drawerPaper: {
      position: "relative",
      whiteSpace: "nowrap",
      width: drawerWidth,
      transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
      }),
      border: "none",
    },
    drawerPaperClose: {
      overflowX: "hidden",
      transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      width: theme.spacing(7),
      [theme.breakpoints.up("sm")]: {
        width: theme.spacing(9),
      },
    },
    snackbar: {
      background: theme.palette.grey["A400"],
      color: "#ffffff",
    },
    snackbarCloseIcon: {
      color: theme.palette.grey[400],
    },
    appBarSpacer: theme.mixins.toolbar as CSSObject,
    mainContainer: {
      display: "flex",
      width: "100vw",
    },
    content: {
      flex: 1,
      height: "100vh",
      overflow: "hidden",
      background: theme.palette.background.paper,
    },
    contentWrapper: {
      height: "100%",
      display: "flex",
      paddingTop: "64px", // app-bar height
      overflow: "scroll",
    },
    sidebarContainer: {
      display: "flex",
      justifyContent: "space-between",
      height: "100%",
      flexDirection: "column",
    },
    listItem: {
      borderTopRightRadius: "24px",
      borderBottomRightRadius: "24px",
    },
  }));

function mapStateToProps(state: AppState) {
  return {
    snackbar: state.snackbar,
    themePreference: state.settings.themePreference,
    isDrawerOpen: state.settings.isDrawerOpen,
  };
}

const mapDispatchToProps = {
  closeSnackbar,
  toggleDrawer,
};

const connector = connect(mapStateToProps, mapDispatchToProps);

function SlideUpTransition(
  props: TransitionProps & { children: React.ReactElement<any, any> }
) {
  return <Slide {...props} direction="up" />;
}

function App(props: ConnectedProps<typeof connector>) {
  const theme = useTheme(props.themePreference);
  const { classes, cx } = useStyles({ theme });
  const paths = getPaths();
  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}>
        <Router>
          <div className={classes.root}>
            <AppBar
              position="absolute"
              className={classes.appBar}
              variant="outlined"
            >
              <Toolbar className={classes.toolbar}>
                <IconButton
                  edge="start"
                  color="inherit"
                  aria-label="open drawer"
                  onClick={props.toggleDrawer}
                  className={classes.menuButton}
                  size="large">
                  <MenuIcon />
                </IconButton>
                {isDarkTheme(theme) ? (
                  <LogoDarkTheme width={200} height={48} />
                ) : (
                  <Logo width={200} height={48} />
                )}
              </Toolbar>
            </AppBar>
            <div className={classes.mainContainer}>
              <Drawer
                variant="permanent"
                classes={{
                  paper: cx(
                    classes.drawerPaper,
                    !props.isDrawerOpen && classes.drawerPaperClose
                  ),
                }}
                open={props.isDrawerOpen}
              >
                <Snackbar
                  anchorOrigin={{ vertical: "bottom", horizontal: "left" }}
                  open={props.snackbar.isOpen}
                  autoHideDuration={6000}
                  onClose={props.closeSnackbar}
                  TransitionComponent={SlideUpTransition}
                >
                  <SnackbarContent
                    message={props.snackbar.message}
                    className={classes.snackbar}
                    action={
                      <IconButton
                        size="small"
                        aria-label="close"
                        color="inherit"
                        onClick={props.closeSnackbar}
                      >
                        <CloseIcon
                          className={classes.snackbarCloseIcon}
                          fontSize="small"
                        />
                      </IconButton>
                    }
                  />
                </Snackbar>
                <div className={classes.appBarSpacer} />
                <div className={classes.sidebarContainer}>
                  <List>
                    <div>
                      <ListItemLink
                        to={paths.HOME}
                        primary="Queues"
                        icon={<BarChartIcon />}
                      />
                      <ListItemLink
                        to={paths.SERVERS}
                        primary="Servers"
                        icon={<DoubleArrowIcon />}
                      />
                      <ListItemLink
                        to={paths.SCHEDULERS}
                        primary="Schedulers"
                        icon={<ScheduleIcon />}
                      />
                      <ListItemLink
                        to={paths.REDIS}
                        primary="Redis"
                        icon={<LayersIcon />}
                      />
                      {window.PROMETHEUS_SERVER_ADDRESS && (
                        <ListItemLink
                          to={paths.QUEUE_METRICS}
                          primary="Metrics"
                          icon={<TimelineIcon />}
                        />
                      )}
                    </div>
                  </List>
                  <List>
                    <ListItemLink
                      to={paths.SETTINGS}
                      primary="Settings"
                      icon={<SettingsIcon />}
                    />
                    <ListItem
                      button
                      component="a"
                      className={classes.listItem}
                      href="https://github.com/hibiken/asynqmon/issues"
                      target="_blank"
                    >
                      <ListItemIcon>
                        <FeedbackIcon />
                      </ListItemIcon>
                      <ListItemText primary="Send Feedback" />
                    </ListItem>
                  </List>
                </div>
              </Drawer>
              <main className={classes.content}>
                <div className={classes.contentWrapper}>
                  <Routes>
                    <Route path={paths.TASK_DETAILS} element={<TaskDetailsView />} />
                    <Route path={paths.QUEUE_DETAILS} element={<TasksView />} />
                    <Route path={paths.SCHEDULERS} element={<SchedulersView />} />
                    <Route path={paths.SERVERS} element={<ServersView />} />
                    <Route path={paths.REDIS} element={<RedisInfoView />} />
                    <Route path={paths.SETTINGS} element={<SettingsView />} />
                    <Route path={paths.HOME} element={<DashboardView />} />
                    <Route path={paths.QUEUE_METRICS} element={<MetricsView />} />
                    <Route path="*" element={<PageNotFoundView />} />
                  </Routes>
                </div>
              </main>
            </div>
          </div>
        </Router>
      </ThemeProvider>
    </StyledEngineProvider>
  );
}

export default connector(App);
