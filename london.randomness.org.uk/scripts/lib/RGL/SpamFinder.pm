package RGL::SpamFinder;

use strict;

use Data::Dumper;
use Email::Send;

sub looks_like_spam {
    my ( $class, %args ) = @_;

    my $name = $args{node};
    my $content = $args{content};
    my $username = $args{metadata}{username};
    my $host = $args{metadata}{host};
    my $comment = $args{added_comment} || "";

    if ( $content =~ /\b(viagra|cialis|supermeganah|tramadol|vicodin|phentermine|buyphentermine|adipex|phendimetrazine|ephedrine|lipitor|hydrocodone|replica-watches|propecia|ativan|levitra|lexapro|ambien|citalopram|effexor|fluoxetine)\b/is ) {
        $class->notify_admins( %args, id => "00002", reason => "Matches $1" );
        return 1;
    }

    my @cats = @{ $args{metadata}{category} };
    foreach my $cat ( @cats ) {
        if ( $cat =~ m'http://'i ) {
            $class->notify_admins( %args, id => "00004",
                                   reason => "URL in category field" );
            return 1;
        }
        if ( $cat =~ m/very nice site!/i ) {
            $class->notify_admins( %args, id => "00005",
                                   reason => "Very Nice Site in category" );
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
             && $comment =~ /you\shave\sa\sgreat\ssite/is ) {
            $class->notify_admins( %args, id => "00015",
                                   reason => "Have a great site on $name" );
            return 1;
        }

        if ( $comment =~ m/(\+.*){7,}/ && $comment !~ m'http://' ) {
            $class->notify_admins( %args, id => "00024",
                                   reason => "comment with more than 7 plus "
                                             . "signs in and no http://" );
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
