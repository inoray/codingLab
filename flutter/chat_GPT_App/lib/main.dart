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
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: () async {
                    Session sess = Session();
                    final resp = await sess
                        .post("https://api.openai.com/v1/chat/completions");
                    print(resp);

                    setState(() {
                      this.txt = resp['choices'][0]['message']['content'];
                    });
                  },
                  child: Text("chatgpt"),
                ),
                Row(
                  children: [
                    Expanded(
                      // child: Markdown(
                      //   data: this.txt,
                      // ),
                      child: DefaultTextStyle(
                        style: const TextStyle(
                            color: Colors.blue,
                            fontWeight: FontWeight.w700,
                            fontSize: 16),
                        child: AnimatedTextKit(
                            isRepeatingAnimation: false,
                            repeatForever: false,
                            displayFullTextOnTap: true,
                            totalRepeatCount: 1,
                            animatedTexts: [
                              TyperAnimatedText(
                                this.txt.trim(),
                              ),
                            ]),
                      ),
                    ),
                  ],
                ),
                // Text(this.txt),
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
    'Authorization':
        'Bearer $openaiKey',
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
      child:
      ListTileTheme(
        contentPadding: const EdgeInsets.all(5),
        iconColor: Colors.red,
        textColor: Colors.black54,
        tileColor: Colors.white,
        style: ListTileStyle.list,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),

        ),
        child: ListView(
          padding: EdgeInsets.zero,
          children: [
            DrawerHeader(
              child: Text('Drawer Header'),
              decoration: BoxDecoration(
                color: Colors.blue,
              ),
            ),
            ListTile(
              title: Text('Item 1'),
              onTap: () {
                // TODO: Handle item 1 press
              },
            ),
            Card(
              margin: const EdgeInsets.all(10),
              color: SIDEBAR_BACKGROUND_COLOR,
              child: ListTile(
                title: Text(
                  "New chat",
                  style: TextStyle(
                    color: SIDEBAR_COLOR,
                  ),
                ),
                onTap: () {
                  // TODO: Handle item 2 press
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
