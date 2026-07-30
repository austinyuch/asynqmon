import React from "react";
import { useTheme } from "@mui/material/styles";
import { makeStyles } from 'tss-react/mui';
import TextField from "@mui/material/TextField";
import Autocomplete from '@mui/material/Autocomplete';
import useMediaQuery from "@mui/material/useMediaQuery";
import ListSubheader from "@mui/material/ListSubheader";
import { List, RowComponentProps } from "react-window";
import { GroupInfo } from "../api";
import { isDarkTheme } from "../theme";

const useStyles = makeStyles()((theme) => ({
  groupSelectOption: {
    display: "flex",
    justifyContent: "space-between",
    width: "100%",
  },
  groupSize: {
    fontSize: "12px",
    color: theme.palette.text.secondary,
    background: isDarkTheme(theme)
      ? "#303030"
      : theme.palette.background.default,
    textAlign: "center",
    padding: "3px 6px",
    borderRadius: "10px",
    marginRight: "2px",
  },
  inputRoot: {
    borderRadius: 20,
    paddingLeft: "12px !important",
  },
}));

interface Props {
  selected: GroupInfo | null;
  onSelect: (newVal: GroupInfo | null) => void;
  groups: GroupInfo[];
  error: string;
}

export default function GroupSelect(props: Props) {
  const { classes } = useStyles();
  const [inputValue, setInputValue] = React.useState("");

  return (
    <Autocomplete
      id="task-group-selector"
      value={props.selected}
      onChange={(_event, newValue: GroupInfo | null) => {
        props.onSelect(newValue);
      }}
      inputValue={inputValue}
      onInputChange={(event, newInputValue) => {
        setInputValue(newInputValue);
      }}
      disableListWrap
      ListboxComponent={
        ListboxComponent as React.ComponentType<
          React.HTMLAttributes<HTMLElement>
        >
      }
      options={props.groups}
      getOptionLabel={(option: GroupInfo) => option.group}
      style={{ width: 300 }}
      renderOption={(liProps, option: GroupInfo) => (
        <li {...liProps} className={classes.groupSelectOption}>
          <span>{option.group}</span>
          <span className={classes.groupSize}>{option.size}</span>
        </li>
      )}
      renderInput={(params) => (
        <TextField {...params} label="Select group" variant="outlined" />
      )}
      classes={{
        inputRoot: classes.inputRoot,
      }}
      size="small"
    />
  );
}

// Virtualized list.
// Reference: https://v4.mui.com/components/autocomplete/#virtualization

const LISTBOX_PADDING = 8; // px
const MAX_VISIBLE_ROWS = 8;

interface VirtualizedRowProps {
  itemData: React.ReactNode[];
}

function renderRow({
  itemData,
  index,
  style,
}: RowComponentProps<VirtualizedRowProps>) {
  return React.cloneElement(itemData[index] as React.ReactElement, {
    style: {
      ...style,
      top: (style.top as number) + LISTBOX_PADDING,
    },
  });
}

export function getVirtualizedChildSize(
  child: React.ReactNode,
  itemSize: number
) {
  if (React.isValidElement(child) && child.type === ListSubheader) {
    return 48;
  }
  return itemSize;
}

export function getVirtualizedListHeight(
  itemData: React.ReactNode[],
  itemSize: number
) {
  if (itemData.length > MAX_VISIBLE_ROWS) {
    return MAX_VISIBLE_ROWS * itemSize;
  }
  return itemData
    .map((child) => getVirtualizedChildSize(child, itemSize))
    .reduce((total, size) => total + size, 0);
}

// Adapter for react-window
const ListboxComponent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLElement>
>(
  function ListboxComponent(props, ref) {
    const { children, ...other } = props;
    const itemData = React.Children.toArray(children);
    const theme = useTheme();
    const smUp = useMediaQuery(theme.breakpoints.up("sm"), { noSsr: true });
    const itemCount = itemData.length;
    const itemSize = smUp ? 36 : 48;

    return (
      <div ref={ref}>
        <List
          {...other}
          rowComponent={renderRow}
          rowCount={itemCount}
          rowHeight={(index) =>
            getVirtualizedChildSize(itemData[index], itemSize)
          }
          rowProps={{ itemData }}
          overscanCount={5}
          tagName="ul"
          style={{
            height:
              getVirtualizedListHeight(itemData, itemSize) +
              2 * LISTBOX_PADDING,
            width: "100%",
          }}
        />
      </div>
    );
  }
);
