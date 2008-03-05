# function to see if a machine exists. if not add it and source the alias file again.
function testmachine {
if grep -q ^$1 ~/.machines
then
echo ""
else
	echo "not in ~/.machines adding"
	echo $1 >> ~/.machines
	source ~/.bash_aliases
fi
}

# open ssh connections in their own xterm. see if it exists in .machines.
function ssh {
xterm -T $1 -e ssh $1 &
testmachine $1
}
# make rdesktop connect as administrator and open at a useful size. detach as well

function rdesktop {
/opt/csw/bin/rdesktop -u administrator -g1200x900 $1 &
}
