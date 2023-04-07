import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:animated_text_kit/animated_text_kit.dart';
import 'package:chat_gpt_app/const/color.dart';
import 'package:chat_gpt_app/component/chatbox.dart';
import 'package:chat_gpt_app/component/sidebar.dart';
import 'package:chat_gpt_app/model/session.dart';
import 'package:chat_gpt_app/component/prompt.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  late List<dynamic> _messages;
  late FocusNode _focusNode;
  late ScrollController _scrollController;
  bool _isLoading = false;
  final _modelList = ['gpt-3.5-turbo'];
  String _selectedModel = 'gpt-3.5-turbo';

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _messages = [
      {"role": "system", "content": "You are a helpful assistant."},
    ];
    _focusNode = FocusNode();
    _scrollController = ScrollController();
    //getModel();
  }

  @override
  Widget build(BuildContext context) {
    // ListView 빌드가 완료된 후 자동으로 스크롤을 제일 아래로 이동 시킨다.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.fastOutSlowIn,
        );
      }
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

              FocusScope.of(context).requestFocus(_focusNode);
            },
          ),
          Expanded(
            child: Stack(
              alignment: Alignment.center,
              children: [
                _messages.length > 1
                    ? Positioned.fill(
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
                              isChatGpt: _messages[index]['role'] == 'user'
                                  ? false
                                  : true,
                            );
                          },
                        ))
                    : Positioned(
                        top: 50,
                        left: MediaQuery.of(context).size.width / 2 - 300,
                        right: MediaQuery.of(context).size.width / 2 - 300,
                        bottom: MediaQuery.of(context).size.height - 100,
                        child: DropdownButton(
                          padding: EdgeInsets.only(
                            left: 10,
                            right: 10,
                          ),
                          value: _selectedModel,
                          items: _modelList
                              .map<DropdownMenuItem<String>>((String value) {
                            return DropdownMenuItem<String>(
                              value: value,
                              child: Text(value),
                            );
                          }).toList(),
                          onChanged: (value) {
                            setState(() {
                              _selectedModel = value!;
                            });
                          },
                        ),
                      ),
                Positioned.fill(
                  bottom: 20,
                  child: Align(
                    alignment: Alignment.bottomCenter,
                    child: Padding(
                      padding: const EdgeInsets.all(10.0),
                      child: Prompt(
                        focusNode: _focusNode,
                        isLoading: _isLoading,
                        onSubmitted: requestChat,
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

  void requestChat(String newPrompt) async {
    if (newPrompt.isNotEmpty) {
      setState(() {
        _isLoading = true;
        _messages.add(
          {'role': "user", 'content': newPrompt},
        );
      });

      Session sess = Session();
      final resp = await sess.postChat(
        _selectedModel,
        _messages,
      );

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
  }

  void getModel() async {
    Session sess = Session();
    final resp = await sess.getModel();
    print(resp);

    setState(() {
      for (int i = 0; i < resp['data'].length; ++i) {
        _modelList.add(resp['data'][i]['id']);
      }
    });
  }
}
