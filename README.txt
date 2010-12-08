This is the code used to generate PDF's from Encoded Archival Description (EAD)
xml file for the Online Archive of California (OAC) website. 

This is organically grown code for PDF generation. The pisa tool was chosen in
order to have the PDF's match the html view of EAD as much as possible.


Known Issues:

Unicode support: Currently characters from non-latin-1 character sets do not
display correctly. I'm working on a patch to bundle an extended font when
necessary to support these characters.

On large EAD (over a few megabytes), this program can take a *very* long time to
run. A timeout function wrapper was introduced to address this when working on
large sets of EAD. Also, see the pdf_gen_by_size.py for a code that runs well on
a large set of EAD.

The timeout function utilizing signals doesn't work on Windows. If running on
windows, you might try commenting out the timeout wrapping code.

Contact me at: mark.redar@ucop.edu.
