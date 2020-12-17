Acoustician: Python Room Acoustics Simulator

This program represents soundwave motion as a series of "balls", dividing
continuous wavefronts into discrete particles for the sake of visualization.
Single frequency pulses can be modelled at 125Hz, 250Hz, 500Hz, 1kHz, 2kHz, and
4kHz. Users define the sound source's location and dispersion angle, any
interior walls, and the materials of all walls. Edge walls are initialized as
smooth unpainted concrete.

Required packages: arcade, numpy, math

Run via command line: "acoustician.py"

-------------------------------------------------------------------------------
Keyboard Controls:
- 1-6: toggles through frequency options
- SPACE: sends soundwave at selected frequency
- E: change edge walls' material
- Quit: program can be ended by typing "quit" while entering any non-list input

To create interior walls, click Make Wall. Then click and drag to define either
a planar wall or the radius of a circular wall.

-------------------------------------------------------------------------------
All absorption measurements are sourced from Acoustic Project Company data
sheets: https://www.acoustic.ua/st/web_absorption_data_eng.pdf

Current material choices:
- Smooth unpainted concrete,
- Plasterboard on battens (18mm airspace with glass wool),
- Muslin-covered cotton felt (25mm thickness),
- Standard brickwork,
- Clinker concrete (no surface finish)

-------------------------------------------------------------------------------
Planned features for future releases:
- Use numpy heatmap as the window background to improve node visualization
- Add the option for a continuous stream of soundwaves instead of a single pulse
- Add the option for image compilation instead of realtime animation
- Adjust interior wall collision detection to treat planar walls as line
    segments with defined thickness rather than infinite planes
- Allow for multiple sound sources
- Implement click-responsive wall selection for editing material or deletion
- Create microphone objects that output a frequency response plot; would track
    the density and frequency of ball objects that pass through their receptive
    fields, similar to a background heatmap; a density log could then also be
    exported as a graph of dB build-up vs. frequency and compiled to show change
    over time
- Using a microphone object, reverb could be modelled by measuring the delay
    between a ball passing through the receptive field and its return after a
    bounce