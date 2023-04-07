import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:chat_gpt_app/const/key.dart';


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
