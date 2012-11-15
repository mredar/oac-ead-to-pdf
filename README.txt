This is the code used to generate PDF's from Encoded Archival Description (EAD)
xml file for the Online Archive of California (OAC) website. 

This is organically grown code for PDF generation. The pisa tool was chosen in
order to have the PDF's match the html view of EAD as much as possible.

This is a refactored release and requires upgrading of a number of libraries.
The new libraries and code correctly handle Unicode characters and will embed the appropriate DejaVuSans font element into the pdf for non latin-1 unicode charaacters.

It also adds the capacity to take advantage of multi-processors with new code in the *parallel.py files. This uses the Parallel Python library to control the multiple processes.

The main code is in pdf_gen.py and should run directly from pdf_gen.py.
The files in the scripts/ directory are more specific to our OAC setup, but they do provide examples of various options.

Known Issues:

On large EAD (over a few megabytes), this program can take a *very* long time to
run. A timeout function wrapper was introduced to address this when working on
large sets of EAD. Also, see the pdf_gen_by_size.py for a code that runs well on
a large set of EAD.

The timeout function utilizing signals doesn't work on Windows. If running on
windows, you might try commenting out the timeout wrapping code.

Contact me at: mark.redar@ucop.edu.
