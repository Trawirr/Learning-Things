import processing.video.*; 

int cols = 5;
int rows = 2;
int tileWidth = 540;
int tileHeight = 960;

int interval = 10000;
int lastTime = 0;

ArrayList<Movie> movies = new ArrayList<Movie>();
int[] moviesIndices = new int[10];

void loadMovies(String directoryPath) {
  File dir = new File(directoryPath);
  if (dir.isDirectory()) { 
    File[] files = dir.listFiles();
    for (File file : files) {
      String filename = file.getName();
      if (filename.endsWith(".mp4")) { 
        Movie movie = new Movie(this, file.getAbsolutePath());
        if (movie != null) {
          movies.add(movie);
          movie.loop();  
          println("Loaded: " + filename);
        }
      }
    }
    for (int i = 0; i < movies.size(); i++) moviesIndices[i] = i;
  } else {
    println("Invalid directory path: " + directoryPath);
  }
}

void shuffle() {
  IntList indicesTmp = new IntList();
  for (int i = 0; i < 10; i++) {
    indicesTmp.append(i);
  }

  Boolean done = false;
  while (!done) {
    done = true;
    indicesTmp.shuffle();
    for (int i = 0; i < 10; i++) {
      if (indicesTmp.get(i) == moviesIndices[i]) {
        done = false;
        break;
      }
    }
  }

  for (int i = 0; i < 10; i++) {
    moviesIndices[i] = indicesTmp.get(i);
  }
}

void playMovies() {
  for (int i = 0; i < 10; i++) {
    if (!movies.get(moviesIndices[i]).isPlaying()) {
      movies.get(moviesIndices[i]).play();
    }
  }
}

void setup() {
  size(2700, 1920);
  loadMovies("path...");
}

void draw() {
  if (millis() - lastTime > interval) {
    shuffle();
    lastTime = millis(); 
  }

  playMovies();

  int index = 0;
  for (int y = 0; y < rows; y++) {
    for (int x = 0; x < cols; x++) {
      Movie movie = movies.get(moviesIndices[index]);
      if (movie.available()) {
        movie.read();  
      }

      pushMatrix();
      translate(x * tileWidth, y * tileHeight);
      rotate(HALF_PI);
      image(movie, 0, -tileWidth, tileHeight, tileWidth);  
      popMatrix();
      
      index++;
    }
  }
}
