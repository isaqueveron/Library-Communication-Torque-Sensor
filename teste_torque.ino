
void setup() {
  // put your setup code here, to run once:
  Serial.begin(230400);
  Serial.setTimeout(30);
  while (!Serial);
}
void loop() {
  String incomingByteString; // para  dados recebidos na porta serial

  // enviar resposta apenas quando receber dados:
  if (Serial.available() > 0) {
  
    // lê o dado recebido:
    incomingByteString = Serial.readString();
    incomingByteString.trim();
    
    Serial.println(incomingByteString);
    
    
  }
}
