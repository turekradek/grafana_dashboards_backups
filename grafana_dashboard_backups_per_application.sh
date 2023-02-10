#!/bin/bash

set -o errexit
set -o pipefail
# set -x
##############################
KEY="USE TOKEN FOR YOUR USER" #USE THE TOKEN THAT WAS CREATED BY TAU FOR YOUR USER
#############################
# script does baskup for grafana dashboard if new configuration file is different then last one
############################
KEY="TOKEN"
FULLURL="https://grafana-centralized-monitoring.advantagedp.org"
headers="Authorization: Bearer $KEY"
in_path=temporary_folder
set -o nounset
#localization="/A/Bstg/user/USER/DIRECTORY/DIRECTORY1/" # LOCALIZATION FOR STAG
localization="/A/Bprod/user/USER/DIRECTORY/DIRECTORY1/" # LOCALIZATION FOR PROD


mkdir -p $in_path
underline="_"
echo "where i am"
pwd
NOW=$( date '+%F-%H-%M-%S' )
sleep 3
# NOW=$( date '+%F' )
echo "this is NOW $NOW"
folder_to_pack=repo_to_copy
#folder_to_pack="$localization${folder_to_pack}"
echo " FOLDER TO PACK =     $folder_to_pack "
mkdir -p "$localization/${folder_to_pack}"
echo " folder to pack created "
pwd
ls
echo " ---- "
ls $localization

# for dash in $(curl -H "$headers" -s "$FULLURL/api/search?query=&" | jq -r '.[] | select(.type == "da$# for dash in $(curl -H "$headers" -s "$FULLURL/api/search" | jq -r '.[] | select(.type == "dash-db") $

folders=("folder1" "folder 2")
function make_backups () {
    for folder in "${folders[@]}";
    do
        echo "folder $folder "
        new_folder="${folder//[ ]/$underline}"
        sleep 1
        echo "new_folder $new_folder"
        new_folder+="_$NOW"
        sleep 1
        echo "new_folder $new_folder"
        # mkdir -p "$new_folder"
        # ls
        # this curl takes all dashboards if folderTitle is equal variable folder  .
        for dash in $(curl -H "$headers" -s "$FULLURL/api/search" | jq -r '.[] | select(.folderTitle == "'"$folder"'" ) $        do

        #       # curl -H "$headers" -s "$FULLURL/api/search?query=&" 1>/dev/null # ZOBACZ CZY DZIALA JAK ZAKOMENUTJE BO$                dash_path="$in_path/$dash.json"
                echo "dash_path          $dash this is uid of dashboard"
                dash_path="$dash.json"
                # this curl takes dashboard with specific dash-uid and write to file with extension json
                curl -H "$headers" -s "$FULLURL/api/dashboards/uid/$dash" | jq -r . > $dash_path ##
                # make json style and write to temporary_folder/dashboard.json name
                jq -r .dashboard $dash_path > $in_path/dashboard.json
                # create new title .dashboard.title for current dashboard file
                title=$(jq -r .dashboard.title $dash_path)
                new_title="${title//[ ]/$underline}";
                new_folder="$new_title"
                new_title+="_"$NOW
                mkdir -p "$new_folder"
                # take last file from folder
                last_file=$new_folder/$(ls -At $new_folder | head -1 )
                current_file=$in_path/dashboard.json
                # echo " ==========$last_file=================$current_file=============================== "
                # cat $current_file > temporary_file1.json
                # cat $last_file > temporary_file2.json
                # cmp file1 file2  # COMPARE TWO FILES
                if  ! cmp $current_file $last_file &>/dev/null ; then
                    echo " ========== CURRENT FILE AND LAST FILE ARE DIFFERENT ============ "
                    echo " ========== I WILL DO BACKUP OF THIS FOLDER  ============ "
                    echo " localization = $localization ,  folder_to_pack = $folder_to_pack , new_title   = $new_title "
                    cp -f $in_path/dashboard.json "$localization/${folder_to_pack}/${new_title}.json"
                    mv -f $in_path/dashboard.json "$new_folder/${new_title}.json"
                fi

                # mv -f $in_path/dashboard.json "$new_folder/${new_title}.json"
            echo "exported $new_folder/${title}.json"


        done

    done
    echo "DONE";


}

make_backups
