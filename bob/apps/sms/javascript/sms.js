zimki.library.require('trimpath.js');

function sms (args){
var meh = setup.get({ name:'main' });
var username = meh.username;
var password = meh.password;
var mobile = args.mobile.replace(/\s+/g, '');
var sms = args.sms ;
var type = "sms";
if (args.type)
type = args.type;

var result = zimki.remote.get ( "http://www.kapow.co.uk/scripts/sendsms.php", { username: username , password: password, mobile: mobile , sms: sms } );

var split = result.match(/(\w+) (\d+)/);


var data = { mobile:mobile, result:split[1], number:split[2], type:type };
var output = zimki.render.trimpath( 'smssend.tp', data );
return output;
}

function wappush (args) { 

var message = "WAPPUSH "+args.sms;
var output = sms ({ username:args.username,  sms:message,  mobile:args.mobile, type:'wappush'});
return output;
}


function smsform() {
return zimki.render.trimpath( 'smsform.tp' );
}
function wappushform() {
return zimki.render.trimpath( 'wappushform.tp');
}

zimki.publishPath('/smssend.html', sms)
zimki.publishPath('/sms.html',smsform)
zimki.publishPath('/wappush.html',wappushform)
zimki.publishPath('/wappushsend.html',wappush)
