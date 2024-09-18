import gifAnimation.*;  
import codeanticode.syphon.*;
SyphonServer server;

int cols = 5;
int rows = 2;
int tileWidth = 540;
int tileHeight = 960;

int interval = 10000;  
int lastTime = 0;

ArrayList<Gif> gifs = new ArrayList<Gif>();  
int[] gifsIndices = new int[10];  

void loadGifs(String directoryPath) {
  File dir = new File(directoryPath);
  if (dir.isDirectory()) { 
    File[] files = dir.listFiles();
    for (File file : files) {
      String filename = file.getName();
      if (filename.endsWith(".gif")) { 
        Gif gif = new Gif(this, file.getAbsolutePath());
        gif.play(); 
        gifs.add(gif);
        println("Loaded: " + filename);
      }
    }
    for (int i = 0; i < gifs.size(); i++) gifsIndices[i] = i;
  } else {
    println("Invalid directory path: " + directoryPath);
  }
}

void shuffle() {
  IntList indicesTmp = new IntList();
  for (int i = 0; i < 10; i++) {
    indicesTmp.append(i);
  }

  boolean done = false;
  while (!done) {
    done = true;
    indicesTmp.shuffle();
    for (int i = 0; i < 10; i++) {
      if (indicesTmp.get(i) == gifsIndices[i]) {
        done = false;
        break;
      }
    }
  }

  for (int i = 0; i < 10; i++) {
    gifsIndices[i] = indicesTmp.get(i);
  }
  println("SHUFFLE TIME");
}

void playGifs() {
  for (int i = 0; i < 10; i++) {
    Gif gif = gifs.get(gifsIndices[i]);
    gif.play(); 
  }
}

void setup() {
  size(2700, 1920);
  loadGifs("path...");
  server = new SyphonServer(this, "wisloujscie_gifs");
}

void draw() {
  println(frameRate, width, height);
  
  if (millis() - lastTime > interval) {
    shuffle();
    lastTime = millis(); 
  }

  playGifs();

  int index = 0;
  for (int y = 0; y < rows; y++) {
    for (int x = 0; x < cols; x++) {
      Gif gif = gifs.get(gifsIndices[index]);

      image(gif, x * tileWidth, y * tileHeight, tileWidth, tileHeight); 

      index++;
    }
  }
  server.sendScreen();
}
