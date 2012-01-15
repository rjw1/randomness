#!/bin/bash

perl -Mlocal::lib >> ~/.bashrc
echo ". ~/.bashrc" >> ~/.profile
eval $(perl -Mlocal::lib)
cpan App::cpanminus

