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

        if ( $name eq "Old Pack Horse, W4 5TF" && $username =~ /^(com)$/is ) {
            $class->notify_admins( %args, reason => "User '$1' editing OPH");
            return 1;
        }

        if ( $args{added_comment} =~ m/(bibi-nibe|akir-nime|niva-tope|mila-yela|lopi-niza|madu-lika|aiva-nima|hite-buri|rews-kimd|kile-bibi|terveron|rexi-vild|reza-blat|lize-vida|dive-luni|lize111|bestgreatworld\.info|greatworldbank\.info|kelia.freehostia.com|jinerbond|nudestar.uni.cc|sexformnude.uni.cc|kamasutranet.co.cc|lipchild|finentikal)/i ) {
            $class->notify_admins( %args, reason => "$1" );
            return 1;
        }

        if ( $name eq "Chuen Cheng Ku, W1D 6PN" && $username =~ /@/ ) {
            $class->notify_admins( %args, reason => "CCK and \@ in username" );
            return 1;
        }

        if ( $name eq "Nicolas, SW6 4ST" && $args{added_comment} =~ m!http://[-.a-z]+\.co.cc(\s|/)! ) {
            $class->notify_admins( %args, reason => ".co.cc, Nicolas SW6" );
            return 1;
        }

        if ( ( $args{added_comment} =~ /http:\/\/.*http:\/\//s )
             || ( $args{added_comment} =~ /https:\/\/.*https:\/\//s )
             || ( $args{added_comment} =~ /a\s+href=.*a\s+href=/s ) ) {
            $class->notify_admins( %args, reason => "comment with more than one URL in" );
            return 1;
        }
        if ( $args{added_comment} =~ m{<a href=\s*></a>}is ) {
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

        if ( $username =~ /^[a-z]+\s[a-z]+$/ ) {
            my $text = "$username $args{added_comment}";
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
