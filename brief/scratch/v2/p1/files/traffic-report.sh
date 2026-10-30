# traffic-report.sh: a quick report on the nginx access log in this folder.
# Run it with:  bash traffic-report.sh | tee report.txt
# A script is just your pipelines saved in a file. Day 7 covers scripts properly.

echo "== Requests"
wc -l < access.log
echo
echo "== Top 5 client IPs"
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -n 5
echo
echo "== Status codes"
awk '{print $9}' access.log | sort | uniq -c | sort -rn
echo
echo "== Server errors (5xx) by path"
awk '$9 >= 500 {print $9, $7}' access.log | sort | uniq -c | sort -rn
echo
echo "== Top 5 paths that returned 404"
awk '$9 == 404 {print $7}' access.log | sort | uniq -c | sort -rn | head -n 5
