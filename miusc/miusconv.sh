#! /bin/bash
#good tools to read audio files metadata and general information
#soxi, metaflac --list, ffprobe -show_stream

#TODO
#convert cue files encode to be easily readable eg <92> to \'
#THINK about saving cue sheet path to a variable instead of grep *.cue or
#find *.cue all the time
#and you already have, so, just use it?
#there another bug when a path have "!" and sed will make operations with it
#throws bash error event not found

#dependencies
#soxi, cuetags, shnsplit

#FLAGS
#set -e 
#set -o pipefail
#set -x
shopt -s extglob

#TRAPS
#trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
#trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT
#trap 'echo removing; rm -f /tmp/to_split' EXIT

#LOG
LOG_FILE=$HOME/.bin/scripts/miusconv.log
LOG_FAILED=$HOME/.bin/scripts/failed.log
exec 3>&1 4>&2 1>>"$LOG_FILE" 2>&1

#GLOBAL VARIABLES
CELL_DIR="$HOME/files/edit/send_cell"
FIND_DIR="$HOME/files/edit"
MOVE_DIR="$HOME/files/edit"
DIR_FILE=
DIR_FILE_POS=1
MUSIC_DIR="$HOME/files/eddit"
declare -A ALBUM_TAGS

#split long-ass file according to .cue file inside split directory
split_file() 
{
    if [ -d "$DIR_FILE" ]; then
        local dir="$DIR_FILE"
    elif [ -f "$DIR_FILE" ]; then
        local dir=$(sed "${DIR_FILE_POS}q;d" "$DIR_FILE")
        ((++DIR_FILE_POS))
    else
        echo "error: your file or directory doesn't exist"
        exit 1
    fi
    
    #TODO confirm if both files below exists
    local cue_file="$(find "$dir" -maxdepth 1 -iname "*.cue"  -print -quit)"
    local audio_file="$(find "$dir" -maxdepth 1 | grep -iP '(\.flac|\.ape|\.wv)$')"
    
    echo "starting to split "$dir"" | tee /dev/fd/3
    shnsplit -d "$dir" -f "$cue_file" -o flac -t "%n %t" "$audio_file"
    if [ "$?" == 0 ]; then
        echo "splitted "$dir"" | tee /dev/fd/3
        mkdir -p "$dir"/old_flac/
        mv "$audio_file" "$dir"/old_flac/
        #needs extglob enabled, exclude pregap from the file selection
        cuetag.sh "$cue_file" "$dir/!(*pregap*).flac"
        
        create_dir "$dir"
        if [ "$?" -ne 0 ]; then
            printf "error in %s\n. post create_dir function." "$dir" |
            tee /dev/fd/3 "$LOG_FAILED"
        fi
            
    else
        if [ -d "$DIR_FILE" ]; then
            printf "error in splitting %s. aborting\n" "$dir" >&3
            exit 1
        fi
        #TODO
        #write that if shnsplit converted some files but didn't concluded the conversion
        #is necessary to delete any new flac files

        #and set new log dir to not_split
        printf "error in splitting %s\n" "$dir" | tee /dev/fd/3 "$LOG_FAILED"
    fi

    #TODO if --default option, stop script here?
        #call function to fill ALBUM_TAGS array with the respective tags

    if [ -f "$DIR_FILE" ]; then
        if [ "$DIR_FILE_POS" -gt "$(wc -l < "$DIR_FILE")" ]; then
            echo "converted all albums inside the file" | tee /dev/fd/3
            exit 0
        else
            split_file
        fi
    else
        echo "success: "$dir" converted" | tee /dev/fd/3
        exit 0
    fi
    

}

create_dir()
{

    local dir="$1"

    discover_tags "$dir"
    if  [ "$?" -ne 0 ]; then
        return 1
    fi

    local target_dir=""$MUSIC_DIR"/flac_albums/"${ALBUM_TAGS[performer]}"/"${ALBUM_TAGS[year]}""${ALBUM_TAGS[album]}""
    mkdir -p "$target_dir"
    
    #really confirms if $target_dit was created
    if [ "$?" == 0 ] && [ -d "$target_dir" ] && [ -z "$(ls -A "$target_dir")" ]; then
    echo "created "$target_dir"" | tee /dev/fd/3
        #escape target_dir [, ? and * to match the excluded directory in find
        local dir_escaped=$(sed 's/[][?*]/\\&/g' <<< "$dir")
        echo "moving files" | tee /dev/fd/3
        find "$dir" \
            -maxdepth 1 -depth ! -iwholename "$dir_escaped"/old_flac | 
            sed '$d;s/ /\\ /g; s/\x27/\\\x27/g' | xargs -I {} mv {} "$target_dir"
    else
        echo "couldn't create new directory "$target_dir"" | tee /dev/fd/3
        return 1
    fi

    return 0
    
}

discover_tags()
{
    #TODO make /*.cue part in greps case insensitive
    #confirm that cue sheet has all information to fill the array
    #in this case, for now, the best way is to don't move all files
    #that have a buggy cue sheet
    #apply sed and awk operations later to both album tags

    local dir="$1"

    #ALBUM_TAGS[year]="$(grep -h 'DATE' "$dir"/*.cue | grep -oP '[0-9]+' | 
    ALBUM_TAGS[year]="$(grep -h 'DATE' "$dir"/*.[Cc][Uu][Ee] | 
                        grep -oP '[0-9]+' | sed '1q' | awk '{$1=$1};1')"
    ALBUM_TAGS[performer]="$(grep -Ph '(^PERFORMER)' "$dir"/*.[Cc][Uu][Ee] |
                grep -oP '(?<=").*(?=")' |
                sed 's/[[:punct:]]//g;1q' | awk '{$1=$1};1')"
    ALBUM_TAGS[album]="$(grep -Ph '(^TITLE)' "$dir"/*.[Cc][Uu][Ee] |
                         grep -oP '(?<=").*(?=")' |
             sed 's/[[(].*//g;s/[[:punct:]]//g;1q' | awk '{$1=$1};1')"

    echo "${ALBUM_TAGS[@]}"

    if [ -z "${ALBUM_TAGS[performer]// }" ] || [ -z "${ALBUM_TAGS[album]// }" ]; then
        echo "cue sheet without all necessary informations. passing $dir." | tee /dev/fd/3
        return 1
    fi
    
    #add whitespace after year
    grep -oP "(?<=^)[0-9]{4}(?=$)" <<< "${ALBUM_TAGS[year]}" && ALBUM_TAGS[year]+=" "
    return 0

}

move_files()
{

#move already splitted directories
#TODO? sometimes cue sheet has a last track entry 'data'. create an exception?

    echo "searching directories to move" | tee /dev/fd/3

    find "$MOVE_DIR" \
        -iname "*.cue" -print | 
        sed 's/ /\\ /g' |
        awk -F '/[^/]*$' '{print $1}' | awk '!x[$0]++' > /tmp/mv_list

    [ -f /tmp/to_move ] && rm /tmp/to_move
    while read; do
        audio_file_number=$(find "$REPLY" | grep -iP '(\.flac|\.ape|\.wv)$' | wc -l)
        cue_tracks_number=$(find "$REPLY" -iname "*.cue" -print -quit | 
                            sed 's/ /\\ /g; s/\x27/\\\x27/g' |
                            xargs grep -oP "(?<=TRACK )[0-9]+" | sort | tail -1)

        if [ "$audio_file_number" -eq "$cue_tracks_number" ]; then
            printf "%s\n" "$REPLY" >> /tmp/to_move
        else
            #don't know if needs this section
            audio_file_number=$(find "$REPLY" -iname "*.flac" |
                                awk -F '/' '{print $NF}' |
                                grep -oP "[0-9]+" | sort | tail -1)
            [ -z "$audio_file_number" ] && audio_file_number=-1
            #TODO warn about data
            #second if to catch "00. pregap" situations
            if [ "$audio_file_number" -eq "$cue_tracks_number" ]; then
                printf "%s\n" "$REPLY" >> /tmp/to_move
            else
                echo ""$REPLY" will not move"
            fi
        fi

    done < /tmp/mv_list

    local yn
    echo "Want to move the files?" | tee /dev/fd/3
    read yn

    case $yn in
        yes)
            echo "starting "$REPLY"" | tee /dev/fd/3
            ;;
        *)
            echo "quitting"
            exit 0
            ;;
    esac
        
    while read; do
        echo "trying "$REPLY"" | tee /dev/fd/3
        create_dir "$REPLY"
        if [ "$?" -ne 0 ]; then
            printf "error in moving %s\n\n" "$REPLY" | tee /dev/fd/3 "$LOG_FAILED"
        else
            printf "success in moving %s\n\n" "$REPLY" | tee /dev/fd/3
        fi

    done < /tmp/to_move

}

find_files() 
{
#way to find all file types before loop to avoid many "or"s in audio_file_number grep
#     -path $HOME/files/edit/music -prune -o \

#set +e because xargs returns 123 when bash doesn't match  anything,
#even if "grep [something] || [ $? == 1 ] to force 0 when don't match
#set -e
#TODO write outputs to terminal like "nothing found", "3 dirs found in /tmp/to_split" e pá

echo "searching directories to split" | tee /dev/fd/3

find "$FIND_DIR" \
    -iname "*.cue" -print | 
    sed 's/ /\\ /g' |
    awk -F '/[^/]*$' '{print $1}' | awk '!x[$0]++' > /tmp/dir_list
    #strip basename eg foo/bar.cue #remove duplicates from list

[ -f /tmp/to_split ] && rm /tmp/to_split
#[ -f /tmp/2notsplit ] && rm /tmp/2notsplit
while read; do
    audio_file_number=$(find "$REPLY" | grep -iP '(\.flac|\.ape|\.wv)$' | wc -l)
    cue_tracks_number=$(find "$REPLY" -iname "*.cue" -print -quit | 
                        sed 's/ /\\ /g; s/\x27/\\\x27/g' | xargs grep -o 'TRACK 02 AUDIO')

    if [ "$audio_file_number" == 1 ] && [ ! -z "$cue_tracks_number" ]; then
        printf "%s\n" "$REPLY" >> /tmp/to_split
       #printf "%s\nnumber of audio files=%s\ncue track 2=%s\n\n" \
       #"$REPLY" "$audio_file_number" "$cue_tracks_number" >> /tmp/2split
    #else
        #printf "%s\n" "$REPLY" >> /tmp/2notsplit
        #printf "%s\nnumber of audio files=%s\ncue track 2=%s\n\n" \
        #"$REPLY" "$audio_file_number" "$cue_tracks_number" >> /tmp/2notsplit
    fi
done < /tmp/dir_list

#set -e

}

mp3() 
{
    
    local dir="$1"     
    local target_dir=""$CELL_DIR"/"$(awk -F / {'print $(NF-1)"'/'"$(NF)'} <<< "$dir")""
    mkdir -p "$target_dir"

    #confirm if has tags
    #make test file var to not repeat 6 lines after?
    while true; do
    local has_tags="$(find "$dir" -iname "*.flac" | tail -1 | 
                      sed 's/ /\\ /g; s/\x27/\\\x27/g' | xargs soxi | sort |
                      grep -Pizo "((?s)album.*?artist.*?title)")"

    if [ -z "$has_tags" ]; then
        echo "files aren't properly tagged" >&3
        #find "$dir" -iname "*.flac" | tail -1 | sed 's/ /\\ /g; s/\x27/\\\x27/g' | 
        #    xargs soxi >&3
        #TODO make option to edit tags yourself
        local yn
        echo "Try to tag the files?" | tee /dev/fd/3
        read yn

        case $yn in
            yes)
                tag "$dir"
                ;;
            *)
                echo "quitting"
                exit 0
                ;;
        esac
    else
        #find a way to comprise the next for in a sole process, and not many iterations
        printf "starting conversion of %s to directory %s\n" "$dir" "$target_dir" >&3
        for i in !(*pregap*).flac; 
            do ffmpeg -i "$i" -qscale:a 0 "$target_dir"/"${i/%flac/mp3}"
        done 1>&3
        #need to confirm success
        echo "ended with success"
        exit 0
    fi
    done
}

tag() 
{

    local dir="$1"
    local cue_file="$(find "$dir" -maxdepth 1 -iname "*.cue"  -print -quit)"
    
    if [ -f "$cue_file" ]; then
        cuetag.sh "$cue_file" !(*pregap*).flac
    fi

}

while [ "$1" ]; do

    case "$1" in
        -h|--help)
            echo help >&3
            exit 0;;

        -d|--default)
            DIR_FILE="$(pwd)"
            split_file
            shift ;;

        -f|--find)
            if [ -d "$2" ]; then
                FIND_DIR="$2" 
                shift
           #else
           #    FIND_DIR="$(pwd)"
            fi
            find_files
            shift ;;

        -b|--batch)
            if [ -f "/tmp/to_split" ]; then
                DIR_FILE="/tmp/to_split"
                shift
            elif [ "${2::1}" == "/" ] && [ -f "$2" ]; then
                DIR_FILE="$2"
                shift; shift
            else 
                echo "error: arguments"
                exit 1
            fi
            split_file
            ;;
        -m)
            move_files
            shift
            ;;

        -c|--mp3)
            mp3 "$(pwd)"
            shift ;;
        *)
            exit 1
            ;;
    esac
done




#list=()
#while IFS= read -r -d $'\0'; do 
#    list+=("$REPLY"); 
#done < <(find $HOME/files/edit -path $HOME/files/edit/music -prune -o -iname "*.cue" -print0)
#
#for (( i = 0; i < ${#list[@]}; i++ )); do
#    list[$i]=$(awk -F '/[^/]*$' '{print $1}' <<< ${list[$i]}); 
#done
#
#dir_list=()
#while IFS= read -r -d $'\0'; do 
#    dir_list+=("$REPLY")
#done < <(awk -F $'\0' '!x[$0]++' <<< $(printf "%s\n" "${list[@]}") | tr '\n' '\0')
#
#while IFS= read -r -d $'\0'; do
#    #REPLY=$(sed 's/ /\\ /' <<< $REPLY)
#    file_number=$(echo "$REPLY" | xargs -I {} find {} | grep -E '(\.flac|\.ape)$' | wc -l)
#    cue_number=$(echo "$REPLY" | xargs -I {} find {} -iname "*.cue" -print -quit | sed 's/ /\\ /g' | xargs grep 'TRACK 02 AUDIO')
#    if [ ! -z "$cue_number" ] && [ "$file_number" == 1 ]; then
#        echo "$REPLY" filenumber="$file_number" cuenumber="$cue_number" >> 2split
#    else
#        echo "$REPLY" filenumber="$file_number" cuenumber="$cue_number" >> 2notsplit
#    fi
#done < <(printf "%s\0" "${dir_list[@]}")
#
#
#
#
#
#    #local test_dir=$DIR_FILE
#    #while [ "$test_dir" != '' ]; do
#    #    local test="$(find "$test_dir" -maxdepth 1 -type d -iname "flac_albums")"
#    #    if [ -z "$test" ]; then
#    #        $DIR_FILE="$(awk -F '/[^/]*$' '{print $1)' <<< "$test_dir")"
#    #    else
