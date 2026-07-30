import React from "react";
import ListSubheader from "@mui/material/ListSubheader";
import { describe, expect, it } from "vitest";
import {
  getVirtualizedChildSize,
  getVirtualizedListHeight,
} from "./GroupSelect";

describe("GroupSelect virtualization sizing", () => {
  const desktopRowHeight = 36;
  const headerHeight = 48;
  const maxVisibleRows = 8;

  it("uses a fixed group-header height and the responsive option height", () => {
    expect(
      getVirtualizedChildSize(
        <ListSubheader>Group</ListSubheader>,
        desktopRowHeight
      )
    ).toBe(headerHeight);
    expect(
      getVirtualizedChildSize(<li>queue</li>, desktopRowHeight)
    ).toBe(desktopRowHeight);
    expect(getVirtualizedChildSize(<li>queue</li>, headerHeight)).toBe(
      headerHeight
    );
  });

  it("caps the viewport at eight responsive rows", () => {
    const items = Array.from({ length: 9 }, (_, index) => (
      <li key={index}>queue-{index}</li>
    ));

    expect(getVirtualizedListHeight(items, desktopRowHeight)).toBe(
      maxVisibleRows * desktopRowHeight
    );
  });

  it("sums mixed row heights when fewer than eight rows are present", () => {
    const items: React.ReactNode[] = [
      <ListSubheader key="header">Group</ListSubheader>,
      <li key="queue">queue</li>,
    ];

    expect(getVirtualizedListHeight(items, desktopRowHeight)).toBe(
      headerHeight + desktopRowHeight
    );
  });
});
