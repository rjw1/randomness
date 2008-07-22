package RGL::SpamFinder;

use strict;

use Data::Dumper;
use Email::Send;

sub looks_like_spam {
    my ( $class, %args ) = @_;

    if ( $args{metadata}{comment} =~ /some grammatical corrections/i ) {
        $class->notify_admins( %args,
                               reason => "'some grammatical corrections'" );
        return 1;
    }

    my $name = $args{node};
    my $content = $args{content};
    my $username = $args{metadata}{username};
    my $host = $args{metadata}{host};
    my $comment = $args{added_comment} || "";

    if ( $content =~ /\b(viagra|cialis|supermeganah|tramadol|vicodin|phentermine|buyphentermine|adipex|phendimetrazine|ephedrine|lipitor|hydrocodone|replica-watches)\b/is ) {
        $class->notify_admins( %args, reason => "Matches $1" );
        return 1;
    }

    if ( $args{metadata}{comment} =~ /http:\/\/.*http:\/\//s ) {
        $class->notify_admins( %args, reason => "URLs in change comment" );
        return 1;
    }

    my @cats = @{ $args{metadata}{category} };
    foreach my $cat ( @cats ) {
        if ( $cat =~ m'http://'i ) {
            $class->notify_admins( %args, reason => "URL in category field" );
            return 1;
        }
        if ( $cat =~ m'\n'i ) {
            $class->notify_admins( %args,
                                   reason => "Bare newline in category" );
            return 1;
        }
    }

    my @locs = @{ $args{metadata}{locale} };
    foreach my $loc ( @locs ) {
        if ( $loc =~ m'http://'i ) {
            $class->notify_admins( %args, reason => "URL in locales field" );
            return 1;
        }
        if ( $loc =~ m'\n'i ) {
            $class->notify_admins( %args,
                                   reason => "Bare newline in locale" );
            return 1;
        }
    }

    # Everything below here only matches if we come via "Add a comment".
    if ( $args{via_add_comment} ) {

        if ( $name eq "News" && $username =~ /^(com|football|w|lyrics)$/is ) {
            $class->notify_admins( %args, reason => "User '$1' editing News");
            return 1;
        }

        if ( $name eq "Old Pack Horse, W4 5TF" && $username =~ /^(com|lyrics)$/is ) {
            $class->notify_admins( %args, reason => "User '$1' editing OPH");
            return 1;
        }

        if ( $username =~ m/(m0wz0a6e8ds|m0wzdgs)/i ) {
            $class->notify_admins( %args, reason => "user: $1" );
            return 1;
        }

        if ( $comment =~ m/(\+.*){8,}/ ) {
            $class->notify_admins( %args,
                        reason => "comment with more than 8 plus signs in" );
            return 1;
        }

        if ( $comment =~ m/(bibi-nibe|akir-nime|niva-tope|mila-yela|lopi-niza|madu-lika|aiva-nima|hite-buri|rews-kimd|kile-bibi|terveron|rexi-vild|reza-blat|lize-vida|dive-luni|lize111|bestgreatworld\.info|greatworldbank\.info|kelia.freehostia.com|jinerbond|nudestar.uni.cc|sexformnude.uni.cc|kamasutranet.co.cc|lipchild|finentikal|pendosegi|staggytheboyscoutsla|fjrf.3vindia.info)/i ) {
            $class->notify_admins( %args, reason => "$1" );
            return 1;
        }

        if ( $name eq "Websites About London" && $comment =~ m/(www.google.us|us.cyworld.com|www.imeem.com|freeiq.com)/ ) {
            $class->notify_admins( %args, reason => "Websites About London, $1" );
            return 1;
        }

        if ( $name eq "Chuen Cheng Ku, W1D 6PN" && $username =~ /@/ ) {
            $class->notify_admins( %args, reason => "CCK and \@ in username" );
            return 1;
        }

        if ( $name eq "Websites About London" && $comment =~ m!groups.google.us! ) {
            $class->notify_admins( %args, reason => "groups.google.us/WAL" );
            return 1;
        }

        if ( $name eq "name" && $comment =~ m/^comment\d,$/ ) {
            $class->notify_admins( %args,
                                   reason => "badly configured spambot" );
            return 1;
        }

        if ( ( $name eq "North Acton Station" || $name eq "Nicolas, SW6 4ST" || $name eq "Old Pack Horse, W4 5TF" || $name eq "Oriental Brasserie, W4 2HD" ) && $comment =~ m!http://[-.a-z0-9]+\.(co.cc|uni.cc|talk4fun.net|297m.com|1vn.biz|aokhost.com|freeweb7.com|myokhost.com|22web.net|totalh.com|10001mb.com|isgreat.org|66ghz.com|iblogger.org|byethost12.com|20xhost.com|yourhelpful.net|fasthoster.info|happyhost.org|by.ru|awardspace.com|awardspace.us|2kool4u.net|your-freehosting.info|150m.com|110mb.com)(\s|/)! ) {
            $class->notify_admins( %args, reason => "$1, $name" );
            return 1;
        }

        if ( $username =~ m'&#' ) {
            $class->notify_admins( %args, reason => "HTML entity in username" );
            return 1;
        }

        if ( ( $comment =~ /http:\/\/.*http:\/\//s )
             || ( $comment =~ /https:\/\/.*https:\/\//s )
             || ( $comment =~ /a\s+href=.*a\s+href=/s ) ) {
            $class->notify_admins( %args, reason => "comment with more than one URL in" );
            return 1;
        }
        if ( $comment =~ m{<a href=\s*></a>}is ) {
            $class->notify_admins( %args, reason => "malformed hyperlink in comment" );
            return 1;
        }
        if ( ( $content =~ /good\s+site\.\s+thank/i )
             || ( $content =~ /cool\s+site\.\s+thank/i )
             || ( $content =~ /useful\s+site\.\s+thank/i )
             || ( $content =~ /nice\s+site\.\s+thank/i ) ) {
            if ( $content =~ 'http://' ) {
                $class->notify_admins( %args, reason => "'nice site' + URL" );
                return 1;
            }
        }

        if ( $username =~ /^\s*spinu\s*$/is
             && $comment =~ /^\s*respect\s*$/is ) {
            $class->notify_admins( %args, reason => "Spinu respects us" );
            return 1;
        }

        if ( $username =~ /^[a-z]+\s[a-z]+$/ ) {
            my $text = "$username $comment";
            if ( $text =~ /q[a-tv-z].*q[a-tv-z]/ ) {
                $class->notify_admins( %args, reason => "two-word lowercase username + two occurrences of q+non-u" );
                return 1;
            }
        }

        if ( $content =~ 'http://' && $content =~ /\banal\b/ && $content =~ /\bsex\b/ ) {
            $class->notify_admins( %args, reason => "'anal' + 'sex' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /\bxanax\b/ ) {
            $class->notify_admins( %args, reason => "'xanax' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /\boxycodone\b/ ) {
            $class->notify_admins( %args, reason => "'oxycodone' + URL" );
            return 1;
        }
        if ( $content =~ 'http://' && $content =~ /free\s+video\s+download/ ) {
            $class->notify_admins( %args, reason => "'free video download' + URL" );
            return 1;
        }
    }
}

sub notify_admins {
    my ( $class, %args ) = @_;
    my $datestamp = localtime( time() );
    my $message = <<EOM;
From: kake\@earth.li
To: kake\@earth.li, bob\@randomness.org.uk
Date: $datestamp
Subject: Attempted spam edit on RGL

Someone just tried to edit RGL, and I said no because it looked like spam.
Here follows a dump of the details:

Reason: $args{reason}

EOM
    $message .= Dumper( \%args );

    my $sender = Email::Send->new( { mailer => "SMTP" } );
    $sender->mailer_args( [ Host => "localhost" ] );
    $sender->send( $message );
}

1;
