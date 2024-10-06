#ssh -p 2222 -i ~/.ssh/bitnami-aws-142964478968.pem -L 3307:172.31.26.160:3306 bitnami@52.19.96.252 &
python manage.py runserver
