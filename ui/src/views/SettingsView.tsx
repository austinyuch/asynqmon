import React, { useState } from "react";
import { connect, ConnectedProps } from "react-redux";
import Container from "@mui/material/Container";
import { makeStyles } from "tss-react/mui";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Slider from "@mui/material/Slider";
import { pollIntervalChange, selectTheme } from "../actions/settingsActions";
import { AppState } from "../store";
import FormControl from "@mui/material/FormControl";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import { ThemePreference } from "../reducers/settingsReducer";

const useStyles = makeStyles()((theme) => ({
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
  },
  paper: {
    padding: theme.spacing(2),
    display: "flex",
    overflow: "auto",
    flexDirection: "column",
  },
  formControl: {
    margin: theme.spacing(1),
    display: "flex",
    justifyContent: "space-between",
    flexDirection: "row",
    alignItems: "center",
  },
  selectEmpty: {
    marginTop: theme.spacing(2),
  },
  select: {
    width: "200px",
  },
}));

function mapStateToProps(state: AppState) {
  return {
    pollInterval: state.settings.pollInterval,
    themePreference: state.settings.themePreference,
  };
}

const mapDispatchToProps = { pollIntervalChange, selectTheme };

const connector = connect(mapStateToProps, mapDispatchToProps);

type PropsFromRedux = ConnectedProps<typeof connector>;

function SettingsView(props: PropsFromRedux) {
  const { classes } = useStyles();

  const [sliderValue, setSliderValue] = useState(props.pollInterval);
  const handleSliderValueChange = (event: any, val: number | number[]) => {
    setSliderValue(val as number);
  };

  const handleSliderValueCommited = (event: any, val: number | number[]) => {
    props.pollIntervalChange(val as number);
  };

  const handleThemeChange = (event: SelectChangeEvent<ThemePreference>) => {
    props.selectTheme(event.target.value as ThemePreference);
  };
  return (
    <Container maxWidth="lg" className={classes.container}>
      <Grid container spacing={3} justifyContent="center">
        <Grid item xs={1} />
        <Grid item xs={6}>
          <Typography variant="h5" color="textPrimary">
            Settings
          </Typography>
        </Grid>
        <Grid item xs={5} />

        <Grid item xs={1} />
        <Grid item xs={6}>
          <Paper className={classes.paper} variant="outlined">
            <Typography color="textPrimary">Polling Interval</Typography>
            <Typography gutterBottom color="textSecondary" variant="subtitle1">
              Web UI will fetch live data with the specified interval
            </Typography>
            <Typography gutterBottom color="textSecondary" variant="subtitle1">
              Currently: Every{" "}
              {sliderValue === 1 ? "second" : `${sliderValue} seconds`}
            </Typography>
            <Slider
              value={sliderValue}
              onChange={handleSliderValueChange}
              onChangeCommitted={handleSliderValueCommited}
              aria-labelledby="continuous-slider"
              valueLabelDisplay="auto"
              step={1}
              marks={true}
              min={2}
              max={20}
            />
          </Paper>
        </Grid>
        <Grid xs={5} />

        <Grid item xs={1} />
        <Grid item xs={6}>
          <Paper className={classes.paper} variant="outlined">
            <FormControl variant="outlined" className={classes.formControl}>
              <Typography color="textPrimary">Dark Theme</Typography>
              <Select
                labelId="theme-label"
                id="theme-selected"
                value={props.themePreference}
                onChange={handleThemeChange}
                label="theme preference"
                className={classes.select}
              >
                <MenuItem value={ThemePreference.SystemDefault}>
                  System Default
                </MenuItem>
                <MenuItem value={ThemePreference.Always}>Always</MenuItem>
                <MenuItem value={ThemePreference.Never}>Never</MenuItem>
              </Select>
            </FormControl>
          </Paper>
        </Grid>
        <Grid item xs={5} />
      </Grid>
    </Container>
  );
}

export default connector(SettingsView);
