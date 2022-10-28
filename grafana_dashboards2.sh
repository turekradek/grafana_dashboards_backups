#!/bin/bash

set -o errexit
set -o pipefail
# set -x
KEY="TOKEN"
FULLURL="https://grafana-centralized-monitoring.advantagedp.org"
headers="Authorization: Bearer $KEY"
in_path=temporary_folder
set -o nounset

echo "Exporting Grafana dashboards from $FULLURL"
mkdir -p $in_path
underline="_"
echo "where i am"
pwd
localization="/mapr/dp.stg.munich/user/devops_apps_pol-s/grafana/dashboards/"
# for dash in $(curl -H "$headers" -s "$FULLURL/api/search?query=&" | jq -r '.[] | select(.type == "dash-db") | .uid');$# for dash in $(curl -H "$headers" -s "$FULLURL/api/search" | jq -r '.[] | select(.type == "dash-db") | .uid'); do
for dash in $(curl -H "$headers" -s "$FULLURL/api/search" | jq -r '.[] | select(.folderTitle == "Boson") | .uid');
do
        curl -H "$headers" -s "$FULLURL/api/search?query=&" 1>/dev/null # ZOBACZ CZY DZIALA JAK ZAKOMENUTJE BO NIC NIE $        # dash_path="$in_path/$dash.json"
        dash_path="$dash.json"
        #echo " co to jest dash $dash"
        curl -H "$headers" -s "$FULLURL/api/dashboards/uid/$dash" | jq -r . > $dash_path
        jq -r .dashboard $dash_path > $in_path/dashboard.json
        title=$(jq -r .dashboard.title $dash_path)
        new_title="${title//[ ]/$underline}";
        folder="$(jq -r '.meta.folderTitle' $dash_path)"
        mkdir -p "$folder"
        mv -f $in_path/dashboard.json "$folder/${new_title}.json"
       echo "exported $folder/${title}.json"

done
rm -r $in_path

lista=()
boson="Boson"
# NOW=$( date '+%F_%H:%M:%S' )
NOW=$( date '+%F' )
echo "TO JEST NOW $NOW"
today_backups_directorie=$boson
today_backups_directorie+="_"
today_backups_directorie+=$NOW
echo $today_backups_directorie;
underline="_"
# echo "${today_backups_directorie/-/"$underline"}";
new_name="${today_backups_directorie//[-]/$underline}";
echo "replace - on _ "
echo "${today_backups_directorie//[-]/$underline}";
ls -l;
echo "new name ls $new_name";
echo $new_name;
mv $boson "${localization}$new_name";
ls -l "${localization}$new_name";
echo "DONE";