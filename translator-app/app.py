[Unit]
Description=Flask Translator App
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/translator-app
ExecStart=/usr/bin/python3 /home/ec2-user/translator-app/app.py
Restart=always

[Install]
WantedBy=multi-user.target
