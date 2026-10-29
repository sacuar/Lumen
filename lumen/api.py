"""Backwards-compatible re-export. The real shim lives in sublime_shim/."""
import sublime_shim

sublime_shim.install()

install  = sublime_shim.install
Region   = sublime_shim.Region
Edit     = sublime_shim.Edit
View     = sublime_shim.View
Window   = sublime_shim.Window
Settings = sublime_shim.Settings