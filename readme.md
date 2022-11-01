# QCM -> PDF converter

Convert a QCM parsed by `qcm_parser` into a pdf

# Usage

```bash
$ python qcm_pdf.py -h
usage: qcm_pdf.py [-h] [-n NB_COPY] [-c] filename

Convert a QCM into different format: PDF or HTML. I need a filepath a number of copy and the option -w or -p

positional arguments:
  filename

options:
  -h, --help            show this help message and exit
  -n NB_COPY, --nb_copy NB_COPY
  -c, --code_present    Do you have codeblocks ? Will crash if set to True and there's no code blocks
```

Convert with :

```bash
$ python qcm_pdf.py -n 35 -c qcm_1nsi_04_fonctions.md
```
