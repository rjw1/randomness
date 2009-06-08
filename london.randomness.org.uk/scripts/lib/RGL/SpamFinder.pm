package RGL::SpamFinder;

use strict;

use Data::Dumper;
use Email::Send;

sub looks_like_spam {
    my ( $class, %args ) = @_;

    if ( $args{metadata}{comment} =~ /some grammatical corrections/i ) {
        $class->notify_admins( %args,
                               id     => "00001",
                               reason => "'some grammatical corrections'" );
        return 1;
    }

    my $name = $args{node};
    my $content = $args{content};
    my $username = $args{metadata}{username};
    my $host = $args{metadata}{host};
    my $comment = $args{added_comment} || "";

    if ( $content =~ /\b(viagra|cialis|supermeganah|tramadol|vicodin|phentermine|buyphentermine|adipex|phendimetrazine|ephedrine|lipitor|hydrocodone|replica-watches|propecia|ativan|levitra|lexapro|ambien|citalopram|effexor|fluoxetine)\b/is ) {
        $class->notify_admins( %args, id => "00002", reason => "Matches $1" );
        return 1;
    }

    if ( $args{metadata}{comment} =~ /http:\/\/.*http:\/\//s ) {
        $class->notify_admins( %args, id => "00003",
                               reason => "URLs in change comment" );
        return 1;
    }

    my @cats = @{ $args{metadata}{category} };
    foreach my $cat ( @cats ) {
        if ( $cat =~ m'http://'i ) {
            $class->notify_admins( %args, id => "00004",
                                   reason => "URL in category field" );
            return 1;
        }
        if ( $cat =~ m'\n'i ) {
            $class->notify_admins( %args, id => "00005",
                                   reason => "Bare newline in category" );
            return 1;
        }
        if ( $cat =~ m/very nice site!/i ) {
            $class->notify_admins( %args, id => "10005",
                                   reason => "Very Nice Site in category" );
            return 1;
        }
    }

    my @locs = @{ $args{metadata}{locale} };
    foreach my $loc ( @locs ) {
        if ( $loc =~ m'http://'i ) {
            $class->notify_admins( %args, id => "00006",
                                   reason => "URL in locales field" );
            return 1;
        }
        if ( $loc =~ m'\n'i ) {
            $class->notify_admins( %args, id => "00007",
                                   reason => "Bare newline in locale" );
            return 1;
        }
    }

    # Everything below here only matches if we come via "Add a comment".
    if ( $args{via_add_comment} ) {

        if ( $name eq "Wasabi, EC2A 1AT"
             && $comment =~ m/(geocities|angelfire).com/is ) {
            $class->notify_admins( %args, id => "00008",
                                   reason => "$1 on Wasabi" );
            return 1;
        }

        if ( $name eq "Category Zone 1 Stations"
             && $comment =~ m/(geocities|angelfire).com/is ) {
            $class->notify_admins( %args, id => "00009",
                                   reason => "$1 on Zone 1 Stations" );
            return 1;
        }

        if ( $name eq "Category Asian Food"
             && $comment =~ m/(geocities|angelfire).com/is ) {
            $class->notify_admins( %args, id => "00010",
                                   reason => "$1 on Asian Food" );
            return 1;
        }

        if ( $username =~ /\@mail\.com/ ) {
            $class->notify_admins( %args, id => "00011",
                                   reason => "\@mail.com editing $name");
            return 1;
        }

        if ( $name eq "Dos Amigos, SE22 8HU"
             && $comment =~ m/(forum.zebulon.fr|swishtalk.com|www.forumfr.com)/ ) {
            $class->notify_admins( %args, id => "00012",
                                   reason => "$1 on $name" );
            return 1;
        }

        if ( $comment =~ m/(www.drugs.com)/ ){
            $class->notify_admins( %args, id => "00013",
                                   reason => "$1 in comment" );
            return 1;
        }

        if ( $name eq "William, SE1 6AD"
             && $comment =~ /i\salso\srecommend\sthis\ssite/is ) {
            $class->notify_admins( %args, id => "00014",
                                   reason => "I also recommend on $name" );
            return 1;
        }

        if ( $name eq "William, SE1 6AD"
             && $comment =~ /you\shave\sa\sgreat\ssite/is ) {
            $class->notify_admins( %args, id => "00015",
                                   reason => "Have a great site on $name" );
            return 1;
        }

        if ( $name eq "News" && $username =~ /^(com|football|w|lyrics)$/is ) {
            $class->notify_admins( %args, id => "00016",
                                   reason => "User '$1' editing News" );
            return 1;
        }

        if ( $name eq "Old Pack Horse, W4 5TF" && $username =~ /^(com|lyrics)$/is ) {
            $class->notify_admins( %args, id => "00017",
                                   reason => "User '$1' editing OPH" );
            return 1;
        }

        if ( $comment =~ m/(Good\s+(post|site),\s+admin.)/ ) {
            $class->notify_admins( %args, id => "00018", reason => "$1" );
            return 1;
        }

        if ( $comment =~ /geocities\.com.*\b(sex|porn|sexy|naked|tits|nude|fucking|fuck|boobs|orgasm)\b/is ) {
            $class->notify_admins( %args, id => "00019",
                                   reason => "$1 on geocities" );
            return 1;
        }

        if ( $comment =~ /uk\.geocities\.com/ && $name =~ /^Category/ ) {
            $class->notify_admins( %args, id => "00020",
                                   reason => "geocities comment on category" );
            return 1;
        }

        if ( $name eq "Woolwich Dockyard Station" ) {
            if ( $comment =~ m/(mybloglog.com|vidilife.com|forums.jolt.co.uk|scam.com|indya.com)/i ) {
                $class->notify_admins( %args, id => "00021",
                                 reason => "$1 on Woolwich Dockyard Station");
                return 1;
            }
        }

        if ( $name eq "Toxophilite" ) {
            if ( $comment =~ m/(xoops.org|scam.com|forums.jolt.co.uk)/i ) {
                $class->notify_admins( %args, id => "00022",
                                       reason => "$1 on Toxophilite" );
                return 1;
            }
        }

        if ( $username =~ m/(m0wz0a6e8ds|m0wzdgs|m0w6e8ds|m0wzds|m0wz0a6eds|m0wz6e8ds|m0wzb6sds|m0wzbs)/i ) {
            $class->notify_admins( %args, id => "00023",
                                   reason => "user: $1" );
            return 1;
        }

        if ( $comment =~ m/(\+.*){7,}/ && $comment !~ m'http://' ) {
            $class->notify_admins( %args, id => "00024",
                                   reason => "comment with more than 7 plus "
                                             . "signs in and no http://" );
            return 1;
        }

        if ( $comment =~ /\b(wernetesa)\b/is ) {
            $class->notify_admins( %args, id => "00025",
                                   reason => "Matches $1" );
            return 1;
        }

        if ( $comment =~ m/(bibi-nibe|akir-nime|niva-tope|mila-yela|lopi-niza|madu-lika|aiva-nima|hite-buri|rews-kimd|kile-bibi|terveron|rexi-vild|reza-blat|lize-vida|dive-luni|lize111|bestgreatworld\.info|greatworldbank\.info|kelia.freehostia.com|jinerbond|nudestar.uni.cc|sexformnude.uni.cc|kamasutranet.co.cc|lipchild|finentikal|pendosegi|staggytheboyscoutsla|fjrf.3vindia.info|forum.gorillamask.net|forum.xnxx.com|cityofbalanga.gov.ph|mybroadband.co.za|forums.epicgames.com|www.tetongravity.com|yedda.com|blackplanet.com|forum.skins.be|yuku.com|brides.com|dumpstersluts.com)/i ) {
            $class->notify_admins( %args, id => "00026", reason => "$1" );
            return 1;
        }

        if ( $comment =~ m/(If\s+a\s+man\s+takes\s+no\s+thought\s+about\s+what\s+is\s+distant)/){
            $class->notify_admins( %args, id => "00027", reason => "$1" );
            return 1;
        }

        if ( $name eq "Websites About London" && $comment =~ m/(www.google.us|us.cyworld.com|www.imeem.com|freeiq.com|vancouver-webpages.com|esnips.com)/ ) {
            $class->notify_admins( %args, id => "00028",
                                   reason => "Websites About London, $1" );
            return 1;
        }

        if ( $name eq "Chuen Cheng Ku, W1D 6PN" && $username =~ /@/ ) {
            $class->notify_admins( %args, id => "00029",
                                   reason => "CCK and \@ in username" );
            return 1;
        }

        if ( $name eq "Websites About London" && $comment =~ m!groups.google.us! ) {
            $class->notify_admins( %args, id => "00030",
                                   reason => "groups.google.us/WAL" );
            return 1;
        }

        if ( $name eq "name" && $comment =~ m/^comment\d,$/ ) {
            $class->notify_admins( %args, id => "00031",
                                   reason => "badly configured spambot" );
            return 1;
        }

        if ( ( $name eq "North Acton Station" || $name eq "Nicolas, SW6 4ST" || $name eq "Old Pack Horse, W4 5TF" || $name eq "Oriental Brasserie, W4 2HD" ) && $comment =~ m!http://[-.a-z0-9]+\.(co.cc|uni.cc|talk4fun.net|297m.com|1vn.biz|aokhost.com|freeweb7.com|myokhost.com|22web.net|totalh.com|10001mb.com|isgreat.org|66ghz.com|iblogger.org|byethost12.com|20xhost.com|yourhelpful.net|fasthoster.info|happyhost.org|by.ru|awardspace.com|awardspace.us|2kool4u.net|your-freehosting.info|150m.com|110mb.com)(\s|/)! ) {
            $class->notify_admins( %args, id => "00032",
                                   reason => "$1, $name" );
            return 1;
        }

        if ( $username =~ m'&#' ) {
            $class->notify_admins( %args, id => "00033",
                                   reason => "HTML entity in username" );
            return 1;
        }

        if ( ( $comment =~ /http:\/\/.*http:\/\//s )
             || ( $comment =~ /https:\/\/.*https:\/\//s )
             || ( $comment =~ /a\s+href=.*a\s+href=/s ) ) {
            $class->notify_admins( %args, id => "00034",
                               reason => "comment with more than one URL in" );
            return 1;
        }
        if ( $comment =~ m{<a href=\s*></a>}is ) {
            $class->notify_admins( %args, id => "00035",
                                  reason => "malformed hyperlink in comment" );
            return 1;
        }
        if ( ( $content =~ /good\s+site\.\s+thank/i )
             || ( $content =~ /cool\s+site\.\s+thank/i )
             || ( $content =~ /useful\s+site\.\s+thank/i )
             || ( $content =~ /nice\s+site\.\s+thank/i ) ) {
            if ( $content =~ 'http://' ) {
                $class->notify_admins( %args, id => "00036",
                                       reason => "'nice site' + URL" );
                return 1;
            }
        }

        if ( $username =~ /^\s*(spinu|specna|nepus|nadsy|weter|prasd|stalo|nabe|papa|wernu)\s*$/is
             && $comment =~ /^\s*respect\s*$/is ) {
            $class->notify_admins( %args, id => "00037",
                                   reason => "$1 respects us" );
            return 1;
        }

        if ( $username =~ /^[a-z]+\s[a-z]+$/ ) {
            my $text = "$username $comment";
            if ( $text =~ /q[a-tv-z].*q[a-tv-z]/ ) {
                $class->notify_admins( %args, id => "00038",
       reason => "two-word lowercase username + two occurrences of q+non-u" );
                return 1;
            }
        }

        if ( $content =~ 'http://' && $content =~ /\banal\b/ && $content =~ /\bsex\b/ ) {
            $class->notify_admins( %args, id => "00039",
                                   reason => "'anal' + 'sex' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /\bxanax\b/ ) {
            $class->notify_admins( %args, id => "00040",
                                   reason => "'xanax' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /\boxycodone\b/ ) {
            $class->notify_admins( %args, id => "00041",
                                   reason => "'oxycodone' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /free\s+video\s+download/ ) {
            $class->notify_admins( %args, id => "00042",
                                   reason => "'free video download' + URL" );
            return 1;
        }
        if ( $comment =~ /news\.insurancemax\.de/ ) {
            $class->notify_admins( %args, id => "00043",
                                   reason => "news.insurancemax.de" );
            return 1;
        }
        if ( $comment =~ /(schulsozialpaedagogik\.ch)/ ) {
            $class->notify_admins( %args, id => "00044", reason => $1 );
            return 1;
        }
        if ( $comment =~ /(www\.svu-hk\.cz)/ ) {
            $class->notify_admins( %args, id => "00045", reason => $1 );
            return 1;
        }
        if ( $comment =~ /(www\.blikum\.com)/ ) {
            $class->notify_admins( %args, id => "00046", reason => $1 );
            return 1;
        }
    }
}

sub notify_admins {
    my ( $class, %args ) = @_;
    my $datestamp = localtime( time() );
    $args{id} ||= "(none)";
    my $message = <<EOM;
From: kake\@earth.li
To: kake\@earth.li, bob\@randomness.org.uk
Date: $datestamp
Subject: Attempted spam edit on RGL

Someone just tried to edit RGL, and I said no because it looked like spam.
Here follows a dump of the details:

Reason: $args{reason}
ID: $args{id}

EOM
    $message .= Dumper( \%args );

    my $sender = Email::Send->new( { mailer => "SMTP" } );
    $sender->mailer_args( [ Host => "localhost" ] );
    $sender->send( $message );
}

1;
