# Can doi khi deploy len server (chang 4)

## Mat khau database
docker-compose.yml dang de MYSQL_ROOT_PASSWORD: root / MYSQL_PASSWORD: dmoj
-> Day la cau hinh dev-local. Server phai doi sang mat khau manh.

## Du lieu phai mang theo (khong tu dong di theo code)
- mysqldump database dmoj
- thu muc problems/ (153MB, khong nam trong git)

## Sau khi them bai moi
Phai chay: docker compose restart judge
Neu khong, bai hien tren web nhung bao "Khong co may cham".
