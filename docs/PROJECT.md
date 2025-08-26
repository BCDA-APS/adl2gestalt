# ADL to Gestalt Converter Project

## Project Description

This project aims to create an **ADL to Gestalt converter** that bridges the gap between legacy MEDM (Motif Editor and Display Manager) screens and modern EPICS display systems. The converter will parse MEDM's ASCII Display List (.adl) files using existing Python parsing infrastructure and transform them into Gestalt layout files (.yml). When processed by Gestalt, these layout files will generate equivalent UI displays in modern formats like caQtDM, CSS-Phoebus, or PyDM. This enables seamless migration from legacy MEDM screens to contemporary EPICS display technologies while preserving the original screen layouts, widget properties, and functionality.

The converter will systematically map each MEDM widget type to its Gestalt equivalent, handling geometry, colors, PVs (Process Variables), and other attributes. By leveraging Pete's existing `adl_parser.py` code and the widget mapping documented in `MEDM_DOC.md`, the converter will provide a reliable path for modernizing EPICS displays without requiring manual recreation of existing screens.
