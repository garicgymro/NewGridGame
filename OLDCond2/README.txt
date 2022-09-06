Important client classes:

SpeakerButtonsPanel (instantiated by speaker_buttons_stage()):
-Where the Sender selects the picture he/she wants to draw.
-THIS IS NOT BEING USED IN THE CURRENT VERSION

DrawingPage (instantiated by speaker_draw_stage()):
-Where the Sender makes his/her grid drawing.

ListenerButtonsPanel (instantiated by listener_choice_stage()):
-Where the Receiver sees the grid drawing makes his/her guess


Notes:

-"Hard mode" means when the timer runs out, a blank grid is sent, forcing 50/50 chance of failure.  When turned off, a partially filled grid can be sent.

-To get human readable grid drawings, run the "texify.py" script from the command line with the name of the results file as its only argument.  This will create a folder with the same name as the results file containing a .tex file.  Compile the .tex file to get a PDF with glance-able drawings for each round.

-There is still some de-crufting to be done.