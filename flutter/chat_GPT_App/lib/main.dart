import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:animated_text_kit/animated_text_kit.dart';
import 'package:chat_gpt_app/const/color.dart';
import 'package:chat_gpt_app/const/key.dart';
import 'package:window_manager/window_manager.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  // Must add this line.
  await windowManager.ensureInitialized();
  WindowOptions windowOptions = const WindowOptions(
    // size: Size(800, 600),
    center: true,
    // backgroundColor: Colors.transparent,
    // skipTaskbar: false,
    // titleBarStyle: TitleBarStyle.hidden,
  );
  windowManager.waitUntilReadyToShow(windowOptions, () async {
    await windowManager.show();
    await windowManager.focus();
  });
  windowManager.setTitle('ChatGPT');
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: HomePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late TextEditingController _controller;

  late List<dynamic> _messages;
  late FocusNode myFocusNode;
  late ScrollController _scrollController;
  bool _isLoading = false;

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _controller = TextEditingController();

    _messages = [
      {"role": "system", "content": "You are a helpful assistant."},
    ];
    myFocusNode = FocusNode();
    _scrollController = ScrollController();
    // _scrollController.addListener(_scrollListener);
  }

  _scrollListener() async {
    if (_scrollController.offset ==
            _scrollController.position.maxScrollExtent &&
        !_scrollController.position.outOfRange) {
      //top
    } else if (_scrollController.offset <=
            _scrollController.position.maxScrollExtent &&
        !_scrollController.position.outOfRange) {
      //bottom
    }
  }

  @override
  Widget build(BuildContext context) {
    // ListView 빌드가 완료된 후 자동으로 스크롤을 제일 아래로 이동 시킨다.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 200),
        curve: Curves.fastOutSlowIn,
      );
    });

    return Scaffold(
      backgroundColor: MAIN_BACKGROUND_COLOR,
      // appBar: AppBar(
      //   title: Text('chat gpt'),
      // ),
      // drawer: SidebarX(
      //
      //   controller: SidebarXController(selectedIndex: 0),
      //   items: const [
      //     SidebarXItem(icon: Icons.home, label: 'Home'),
      //     SidebarXItem(icon: Icons.search, label: 'Search'),
      //   ],
      // ),
      // drawer: SideBar(),

      body: Row(
        children: [
          SideBar(
            onPressedNewChat: () {
              setState(() {
                _messages = [
                  {"role": "system", "content": "You are a helpful assistant."},
                ];
              });
            },
          ),
          Expanded(
            child: Stack(
              alignment: Alignment.center,
              children: [
                Positioned.fill(
                  bottom: 100,
                  child: ListView.builder(
                    scrollDirection: Axis.vertical,
                    shrinkWrap: true,
                    controller: _scrollController,
                    padding: EdgeInsets.zero,
                    itemCount: _messages.length,
                    itemBuilder: (
                      BuildContext context,
                      int index,
                    ) {
                      if (index == 0) return SizedBox();
                      return ChatBox(
                        content: _messages[index]['content'],
                        isChatGpt:
                            _messages[index]['role'] == 'user' ? false : true,
                      );
                    },
                  ),
                ),
                // Column(
                //   mainAxisAlignment: MainAxisAlignment.center,
                //   children: [
                //     // ElevatedButton(
                //     //   onPressed: () async {
                //     //   },
                //     //   child: Text("chatgpt"),
                //     // ),
                //     Row(
                //       children: [
                //         Expanded(
                //           // child: Markdown(
                //           //   data: this.txt,
                //           // ),
                //           child: DefaultTextStyle(
                //             style: const TextStyle(
                //               color: Colors.blue,
                //               fontWeight: FontWeight.w700,
                //               fontSize: 16,
                //             ),
                //             child: AnimatedTextKit(
                //               isRepeatingAnimation: false,
                //               repeatForever: false,
                //               displayFullTextOnTap: true,
                //               totalRepeatCount: 1,
                //               animatedTexts: [
                //                 TyperAnimatedText(
                //                   this.txt.trim(),
                //                 ),
                //               ],
                //             ),
                //           ),
                //         ),
                //       ],
                //     ),
                //     // Text(this.txt),
                //   ],
                // ),
                Positioned.fill(
                  bottom: 20,
                  child: Align(
                    alignment: Alignment.bottomCenter,
                    child: Padding(
                      padding: const EdgeInsets.all(10.0),
                      child: TextField(
                        // enabled: _isLoading ? false : true,
                        readOnly: _isLoading ? true : false,
                        keyboardType: TextInputType.multiline,
                        maxLines: null,
                        autofocus: true,
                        focusNode: myFocusNode,
                        textInputAction: TextInputAction.done,
                        onSubmitted: (value) async {
                          request();
                        },
                        style: TextStyle(color: MAIN_TEXT_COLOR),
                        cursorColor: Colors.white,
                        controller: _controller,
                        decoration: InputDecoration(
                          // labelText: 'Input',
                          filled: true,
                          fillColor: TEXTFILED_BACKGROUND_COLOR,
                          // border: OutlineInputBorder(
                          //     borderSide: BorderSide(width: 1, color: Color(0xff40414f)),
                          // ),
                          enabledBorder: OutlineInputBorder(
                            borderSide: BorderSide(
                                width: 0, color: TEXTFILED_BACKGROUND_COLOR),
                          ),
                          focusedBorder: OutlineInputBorder(
                            borderSide: BorderSide(
                                width: 0, color: TEXTFILED_BACKGROUND_COLOR),
                          ),
                          suffixIcon: SizedBox(
                            width: 10,
                            height: 10,
                            child: _isLoading
                                ? SpinKitThreeBounce(
                                    color: MAIN_TEXT_COLOR,
                                    size: 15.0,
                                  )
                                : IconButton(
                                    alignment: Alignment.centerRight,
                                    icon: const Icon(Icons.send_outlined),
                                    color: MAIN_TEXT_COLOR,
                                    onPressed: () async {
                                      request();
                                    },
                                  ),
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void request() async {
    if (_controller.text.isNotEmpty) {
      setState(() {
        _isLoading = true;
        _messages.add(
          {'role': "user", 'content': _controller.text},
        );
      });

      _controller.clear();
      Session sess = Session();
      final resp = await sess.post(
          "https://api.openai.com/v1/chat/completions", _messages);

      print(resp);

      setState(() {
        _isLoading = false;
        _messages.add(
          {
            'role': "assistant",
            'content': resp['choices'][0]['message']['content']
          },
        );
      });
    }
    // ignore: use_build_context_synchronously
    FocusScope.of(context).requestFocus(myFocusNode);
  }
}

class Session {
  Future<dynamic> post(String strUrl, List<dynamic> messages) async {
    Map<String, String> headers = {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $openaiKey',
    };

    Map<String, dynamic> body = {
      'model': 'gpt-3.5-turbo',
      // 'model': 'gpt-4-32k-0314',
      'messages': messages,
    };

    var url = Uri.https(
      "api.openai.com",
      "/v1/chat/completions",
    );

    final resp = await http.post(
      url,
      headers: headers,
      body: jsonEncode(body),
    );

    // Map<String, String> headers2 = {
    //   'Authorization': 'Bearer $openaiKey',
    // };
    //
    // var url2 = Uri.https(
    //   "api.openai.com",
    //   "/v1/models",
    // );
    //
    // final resp = await http.get(
    //   url2,
    //   headers: headers2,
    // );
    // print(resp);

    final int statusCode = resp.statusCode;
    if (statusCode < 200 || statusCode > 400) {
      print('statusCode: $statusCode');
    }

    var jsonResponse =
        jsonDecode(utf8.decode(resp.bodyBytes)) as Map<String, dynamic>;

    return jsonResponse;
  }
}

class SideBar extends StatelessWidget {
  final VoidCallback onPressedNewChat;

  const SideBar({
    Key? key,
    required this.onPressedNewChat,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Drawer(
      width: 260,
      backgroundColor: SIDEBAR_BACKGROUND_COLOR,
      child: Column(
        children: [
          const SizedBox(height: 10.0),
          SideBarButton(
            icon: Icons.add,
            label: "New chat",
            isBorder: true,
            onPressed: onPressedNewChat,
          ),
          Expanded(
            child: ListTileTheme(
              contentPadding: const EdgeInsets.only(left: 10.0),
              iconColor: MAIN_TEXT_COLOR,
              textColor: MAIN_TEXT_COLOR,
              tileColor: SIDEBAR_BACKGROUND_COLOR,
              // selectedColor: Colors.white,
              // selectedTileColor: Colors.white,
              style: ListTileStyle.list,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(5),
                side: BorderSide(color: SIDEBAR_LINE),
              ),
              horizontalTitleGap: 5.0,
              // minVerticalPadding: 6.0,
              minLeadingWidth: 30.0,
              child: ListView(
                padding: EdgeInsets.zero,
                children: [
                  //SideBarAddButton(),
                ],
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(left: 8.0, right: 8.0),
            child: Divider(
              thickness: 1,
              color: SIDEBAR_LINE,
            ),
          ),
          SideBarButton(
            icon: Icons.wb_sunny_outlined,
            label: "Light mode",
            isBorder: false,
            onPressed: () {},
          ),
          SideBarButton(
            icon: Icons.person_outline,
            label: "My account",
            isBorder: false,
            onPressed: () {},
          ),
          SideBarButton(
            icon: Icons.open_in_new_outlined,
            label: "Updates & FAQ",
            isBorder: false,
            onPressed: () {},
          ),
          SideBarButton(
            icon: Icons.logout_outlined,
            label: "Log out",
            isBorder: false,
            onPressed: () {},
          ),
        ],
      ),
    );
  }
}

class SideBarCard extends StatelessWidget {
  const SideBarCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(left: 8, right: 8, top: 4, bottom: 4),
      color: SIDEBAR_BACKGROUND_COLOR,
      child: SizedBox(
        height: 50,
        child: ListTile(
          // visualDensity: VisualDensity(vertical: -4),
          hoverColor: Color(0xFF2b2c2f),

          leading: const Icon(
            Icons.add,
            size: 20,
          ),
          title: const Text(
            "New chat",
            style: TextStyle(fontSize: 14),
          ),
          onTap: () {
            // TODO: Handle item 2 press
          },
        ),
      ),
    );
  }
}

class SideBarButton extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isBorder;
  final VoidCallback onPressed;
  //typedef VoidCallback = void Function()

  const SideBarButton({
    Key? key,
    required this.label,
    required this.icon,
    required this.isBorder,
    required this.onPressed,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(
        left: 8.0,
        right: 8.0,
        bottom: 4.0,
      ),
      child: SizedBox(
        width: double.infinity,
        height: 50.0,
        child: ElevatedButton.icon(
          onPressed: onPressed,
          icon: Icon(
            icon,
            size: 20,
          ),
          label: Text(label),
          style: ElevatedButton.styleFrom(
            backgroundColor: SIDEBAR_BACKGROUND_COLOR,
            elevation: 0.0,
            alignment: Alignment.centerLeft,
            foregroundColor: MAIN_TEXT_COLOR,
            side: isBorder
                ? BorderSide(
                    width: 1.0,
                    color: SIDEBAR_LINE,
                  )
                : null,
          ),
        ),
      ),
    );
  }
}

class ChatBox extends StatelessWidget {
  final String content;
  final bool isChatGpt;

  const ChatBox({
    Key? key,
    required this.content,
    required this.isChatGpt,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.only(
        left: 50,
        right: 50,
        top: 30,
        bottom: 30,
      ),
      color: isChatGpt ? Color(0xFF444654) : Colors.transparent,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Image.asset(
            isChatGpt ? "asset/chatgpt-icon.png" : 'asset/user.png',
            width: 40.0,
          ),
          const SizedBox(width: 20.0),
          Expanded(
            child: SelectableText(
              content,
              style: TextStyle(
                color: MAIN_TEXT_COLOR,
                fontSize: 17.0,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
