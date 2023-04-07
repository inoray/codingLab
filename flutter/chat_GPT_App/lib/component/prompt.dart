import 'package:flutter/material.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:chat_gpt_app/const/color.dart';

class Prompt extends StatefulWidget {
  final FocusNode focusNode;
  final bool isLoading;
  final ValueChanged<String>? onSubmitted;

  const Prompt({
    Key? key,
    required this.focusNode,
    required this.isLoading,
    required this.onSubmitted,
  }) : super(key: key);

  @override
  State<Prompt> createState() => _PromptState();
}

class _PromptState extends State<Prompt> {
  late TextEditingController _controller;

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _controller = TextEditingController();
  }

  @override
  Widget build(BuildContext context) {
    return TextField(
      // enabled: _isLoading ? false : true,
      readOnly: widget.isLoading ? true : false,
      keyboardType: TextInputType.multiline,
      maxLines: null,
      autofocus: true,
      focusNode: widget.focusNode,
      textInputAction: TextInputAction.done,
      onSubmitted: (value) async {
        submit();
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
          borderSide: BorderSide(width: 0, color: TEXTFILED_BACKGROUND_COLOR),
        ),
        focusedBorder: OutlineInputBorder(
          borderSide: BorderSide(width: 0, color: TEXTFILED_BACKGROUND_COLOR),
        ),
        suffixIcon: SizedBox(
          width: 10,
          height: 10,
          child: widget.isLoading
              ? SpinKitThreeBounce(
                  color: MAIN_TEXT_COLOR,
                  size: 15.0,
                )
              : IconButton(
                  alignment: Alignment.centerRight,
                  icon: const Icon(Icons.send_outlined),
                  color: MAIN_TEXT_COLOR,
                  onPressed: () async {
                    submit();
                  },
                ),
        ),
      ),
    );
  }

  void submit() async {
    widget.onSubmitted!(_controller.text);
    _controller.clear();
  }
}
