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
function ssh {
xterm -T $1 -e ssh $1 &
testmachine $1
}
