import 'package:flutter/material.dart';
import 'package:chat_gpt_app/const/color.dart';

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
