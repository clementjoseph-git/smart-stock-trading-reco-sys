import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(SmartTradeApp());

class SmartTradeApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: SentimentScreen(),
    );
  }
}

class SentimentScreen extends StatefulWidget {
  @override
  _SentimentScreenState createState() => _SentimentScreenState();
}

class _SentimentScreenState extends State<SentimentScreen> {
  final TextEditingController _controller = TextEditingController();
  String _result = "";

  Future<void> analyzeSentiment() async {
    final response = await http.post(
      Uri.parse("http://127.0.0.1:8000/sentiment?text=${_controller.text}"),
    );
    setState(() {
      _result = response.body;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Smart Stock Trading")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(controller: _controller, decoration: InputDecoration(labelText: "Enter news headline")),
            ElevatedButton(onPressed: analyzeSentiment, child: Text("Analyze")),
            SizedBox(height: 20),
            Text(_result),
          ],
        ),
      ),
    );
  }
}
