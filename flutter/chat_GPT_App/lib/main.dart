import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:animated_text_kit/animated_text_kit.dart';
import 'package:chat_gpt_app/const/color.dart';
import 'package:chat_gpt_app/const/key.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
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
  String txt = "";
  @override
  Widget build(BuildContext context) {
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
      drawer: SideBar(),

      body: Row(
        children: [
          SideBar(),
          Expanded(
            child: Stack(
              alignment: Alignment.center,
              children: [
                ListView(
                  padding: EdgeInsets.zero,
                  children: [
                    ChatBox(
                      content: "안녕하세요.",
                      isChatGpt: false,
                    ),
                    ChatBox(
                      content: "반갑습니다.\n어디세요?",
                      isChatGpt: true,
                    ),
                  ],
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
                      padding: const EdgeInsets.all(8.0),
                      child: TextField(
                        decoration: InputDecoration(
                          // labelText: 'Input',
                          fillColor: Colors.white,
                          border: OutlineInputBorder(),
                          suffixIcon: Container(
                            child: IconButton(
                              alignment: Alignment.centerRight,
                              icon: Icon(Icons.send_outlined),
                              onPressed: () async {
                                Session sess = Session();
                                final resp = await sess.post(
                                    "https://api.openai.com/v1/chat/completions");
                                print(resp);

                                setState(() {
                                  this.txt =
                                      resp['choices'][0]['message']['content'];
                                });
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
}

class Session {
  Map<String, String> headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer $openaiKey',
  };
  Map<String, dynamic> body = {
    'model': 'gpt-3.5-turbo',
    'messages': [
      {"role": "user", "content": "Flutter Markdown example"}
    ],
  };

  Future<dynamic> post(String strUrl) async {
    print('get() url: $strUrl');

    var url = Uri.https(
      "api.openai.com",
      "/v1/chat/completions",
    );

    final resp = await http.post(
      url,
      headers: headers,
      body: jsonEncode(body),
    );

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
  const SideBar({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Drawer(
      width: 260,
      backgroundColor: SIDEBAR_BACKGROUND_COLOR,
      child: Column(
        children: [
          Expanded(
            child: ListTileTheme(
              contentPadding: const EdgeInsets.only(left: 10.0),
              iconColor: SIDEBAR_TEXT_COLOR,
              textColor: SIDEBAR_TEXT_COLOR,
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
                  SideBarCard(),
                  SideBarCard(),
                  SideBarCard(),
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
          ),
          SideBarButton(
            icon: Icons.person_outline,
            label: "My account",
          ),
          SideBarButton(
            icon: Icons.open_in_new_outlined,
            label: "Updates & FAQ",
          ),
          SideBarButton(
            icon: Icons.logout_outlined,
            label: "Log out",
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

          leading: Icon(
            Icons.add,
            size: 20,
          ),
          title: Text(
            "New chat",
            style: TextStyle(fontSize: 14),
            // textAlign: TextAlign.center,
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
  const SideBarButton({
    Key? key,
    required this.label,
    required this.icon,
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
          onPressed: () {},
          icon: Icon(icon),
          label: Text(label),
          style: ElevatedButton.styleFrom(
            backgroundColor: SIDEBAR_BACKGROUND_COLOR,
            elevation: 0.0,
            alignment: Alignment.centerLeft,
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
      padding: EdgeInsets.only(
        left: 50,
        right: 50,
        top: 30,
        bottom: 30,
      ),
      child: Text(
        content,
        style: TextStyle(
          color: Colors.white,
        ),
      ),
      color: isChatGpt ? Color(0xFF444654) : Colors.transparent,
    );
  }
}
