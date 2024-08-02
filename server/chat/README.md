* 在运行此工程之前，请先运行该项目的前置依赖项目 **vits-simple-api**
* 在 **chat/main.py** 中运行主程序
* 想要开发应用，请在 **applications_realize** 目录下建立应用的目录，在 **chat/applications.py** 中注册所有可供AI自动调用的静态方法，
  **不管用没用到，方法的第一个参数必须是 user_id** ，并在
  **conf/applications.json** 中对每一个注册过的方法进行json格式的详细解释，具体的细节可以参考示例应用 **send_email**
  的实现方式
* 请在 **conf/settings.json** 中进行项目的各项配置