for MACHINE in `cat ~/.machines`
do
alias $MACHINE="xterm -T $MACHINE -e ssh $MACHINE &"
done
