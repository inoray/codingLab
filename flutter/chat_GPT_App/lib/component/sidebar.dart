import 'package:flutter/material.dart';
import 'package:chat_gpt_app/const/color.dart';
import 'package:chat_gpt_app/component/sidebar_button.dart';

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
