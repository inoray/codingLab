import 'package:flutter/material.dart';
import 'package:chat_gpt_app/const/color.dart';

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

              // child: Markdown(
              //   data: this.txt,
              // ),
              //AnimatedTextKit(
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
            ),
          ),
        ],
      ),
    );
  }
}
