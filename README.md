<h1>Acoustician: Python Room Acoustics Simulator</h1>

This program represents soundwave motion as a series of "balls", dividing
continuous wavefronts into discrete particles for the sake of visualization.
Single frequency pulses can be modelled at 125Hz, 250Hz, 500Hz, 1kHz, 2kHz, and
4kHz. Users define the sound source's location and dispersion angle, any
interior walls, and the materials of all walls. Edge walls are initialized as
smooth unpainted concrete.

Required packages: arcade, numpy, math

Run via command line: <code>acoustician.py</code>

-------------------------------------------------------------------------------
To create interior walls, click Make Wall. Then click and drag to define either
a planar wall or the radius of a circular wall.

Keyboard Controls:
<li>1-6: toggles through frequency options</li>
<li>SPACE: sends soundwave at selected frequency</li>
<li>E: change edge walls' material</li>
<li>Quit: program can be ended by typing "quit" while entering any non-list input</li>

-------------------------------------------------------------------------------
All absorption measurements are sourced from Acoustic Project Company data
sheets: https://www.acoustic.ua/st/web_absorption_data_eng.pdf

Current material choices:
<li>Smooth unpainted concrete,</li>
<li>Plasterboard on battens (18mm airspace with glass wool),</li>
<li>Muslin-covered cotton felt (25mm thickness),</li>
<li>Standard brickwork,</li>
<li>Clinker concrete (no surface finish)</li>

-------------------------------------------------------------------------------
Planned features for future releases:
<li>Use numpy heatmap as the window background to improve node visualization</li>
<li>Add the option for a continuous stream of soundwaves instead of a single pulse</li>
<li>Add the option for image compilation instead of realtime animation</li>
<li>Adjust interior wall collision detection to treat planar walls as line
    segments with defined thickness rather than infinite planes</li>
<li>Allow for multiple sound sources</li>
<li>Implement click-responsive wall selection for editing material or deletion</li>
<li>Create microphone objects that output a frequency response plot; would track
    the density and frequency of ball objects that pass through their receptive
    fields, similar to a background heatmap; a density log could then also be
    exported as a graph of dB build-up vs. frequency and compiled to show change
    over time</li>
<li>Using a microphone object, reverb could be modelled by measuring the delay
    between a ball passing through the receptive field and its return after a
    bounce</li>
