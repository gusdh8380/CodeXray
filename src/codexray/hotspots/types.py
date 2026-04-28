from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FileHotspot:
    path: str
    change_count: int
    coupling: int
    category: str  # "hotspot" | "active_stable" | "neglected_complex" | "stable"


@dataclass(frozen=True, slots=True)
class Thresholds:
    change_count_median: int
    coupling_median: int


@dataclass(frozen=True, slots=True)
class Summary:
    hotspot: int
    active_stable: int
    neglected_complex: int
    stable: int


@dataclass(frozen=True, slots=True)
class HotspotsReport:
    schema_version: int
    thresholds: Thresholds
    summary: Summary
    files: tuple[FileHotspot, ...]
