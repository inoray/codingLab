import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:animated_text_kit/animated_text_kit.dart';
import 'package:chat_gpt_app/const/color.dart';
import 'package:chat_gpt_app/component/chatbox.dart';
import 'package:chat_gpt_app/component/sidebar.dart';
import 'package:chat_gpt_app/model/session.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
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

              FocusScope.of(context).requestFocus(myFocusNode);
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

      // print(resp);

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