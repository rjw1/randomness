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

    if ( $content =~ /\b(viagra|cialis|supermeganah|tramadol|vicodin|phentermine|buyphentermine|adipex|phendimetrazine|ephedrine|lipitor|hydrocodone|replica-watches|propecia|ativan|levitra|lexapro|ambien|citalopram|effexor|fluoxetine|prozac|kamagra|accutane|zithromax|clenbuterol|nolvadex|lorazepam|clonazepam|diazepam|valium|clomid|rimonabant|xenical|lolita|lolitas)\b/is ) {
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

        if ( $comment =~ m/(http.*\.co\.cc\/sitemap)/ ){
            $class->notify_admins( %args, id => "00014",
                                   reason => "$1 in comment" );
            return 1;
        }

        if ( $comment =~ m/(http.*\.tk\/sitemap)/ ){
            $class->notify_admins( %args, id => "00015",
                                   reason => "$1 in comment" );
            return 1;
        }

        if ( $comment =~ m/(http.*ryjgy.edu.ms\/sitemap)/ ){
            $class->notify_admins( %args, id => "00016",
                                   reason => "$1 in comment" );
            return 1;
        }

        if ( $host eq "93.126.94.14" && $name eq "Category Pool Table" ) {
            $class->notify_admins( %args, id => "00017",
                                   reason => "$host comment on $name" );
            return 1;
        }

        if ( $name eq "Old Salt Quay, SE16 5QU" && $comment =~ /www\.soundclick\.com/ ) {
            $class->notify_admins( %args, id => "00018",
                                   reason => "soundclick comment on $name" );
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
