import 'package:flutter/material.dart';
import 'package:chat_gpt_app/const/color.dart';

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
