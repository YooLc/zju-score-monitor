# zju-score-monitor

考试周出分成绩查询小助手

因为太菜了，不会写统一身份认证登录，所以引用了 [zjuyfy/zjuam](https://github.com/zjuyfy/zjuam) 这个项目，感谢大佬。

# 使用方法

1. 安装 Python 的依赖
```bash
pip install -r requirements.txt
```
2. 修改 `monitor.py` 中的 `USERNAME` 和 `PASSWORD` 为你的浙江大学统一身份认证学号和密码。 把 `CURRENT_SEMESTER` 改成当前学年，比如 `2022-2023`。

3. 创建一个只有自己的钉钉群，然后按照 [钉钉自定义机器人接入](https://open.dingtalk.com/document/orgapp/custom-robot-access) 中的前三步添加一个自定义机器人，并修改 `ACCESS_TOKEN` 为你 webhook 网址中 `access_token=` 后面的部分，然后把 `SECRET` （就是前面教程中第三步里加签的内容）填上。

4. 使用 crontab 或者其他计划任务的方式定时执行 `python monitor.py` 即可

# 注意

1. 你需要一个服务器 / NAS / 树莓派之类的能 24h 在线的机器来定时运行这个脚本

2. 你的密码会明文存储在 `monitor.py` 里，请确保这个文件只能被你读取

3. 你的历史成绩（因为要检测变动）会存储在 `preList.json` 中，也请确保这个文件只能被你读取

4. 代码写的不好，欢迎大佬们批评指正 orz