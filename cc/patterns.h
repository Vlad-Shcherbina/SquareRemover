
template<typename K, typename V>
V get_default(const map<K, V> &m, const K &k, const V &def) {
  auto i = m.find(k);
  if (i == m.end())
    return def;
  return i->second;
}


struct PatternInstance {
  int idxs[4];
  vector<Move> moves;

  bool match(const State &s) const {
    char c = s.cells[idxs[0]];
    return
        c == s.cells[idxs[1]] &&
        c == s.cells[idxs[2]] &&
        c == s.cells[idxs[3]];
  }
};


struct Pattern {
  map<int, int> orig_locs;
  int i1, j1, i2, j2;

  vector<int> moves;

  static bool is_center(int idx) {
    return idx == 44 || idx == 45 || idx == 54 || idx == 55;
  }

  void cleanup() {
    vector<int> to_delete;
    for (auto kv : orig_locs)
      if (kv.first == kv.second && !is_center(kv.first))
        to_delete.push_back(kv.first);
    for (int k : to_delete)
      orig_locs.erase(k);
  }


  bool make_move(int mv) {
    int idx = mv & ~VERT;
    int idx2 = idx + 1;
    if (mv & VERT)
      idx2 = idx + 10;
    if (is_center(get_default(orig_locs, idx, idx)) &&
        is_center(get_default(orig_locs, idx2, idx2)))
      return false;

    if (!is_center(get_default(orig_locs, idx, idx)) &&
        !is_center(get_default(orig_locs, idx2, idx2)))
      return false;

    int t = get_default(orig_locs, idx, idx);
    orig_locs[idx] = get_default(orig_locs, idx2, idx2);
    orig_locs[idx2] = t;

    i1 = min(i1, idx / 10);
    j1 = min(j1, idx % 10);
    i2 = max(i2, idx2 / 10 + 1);
    j2 = max(j2, idx2 % 10 + 1);

    moves.push_back(mv);
    cleanup();
    return true;
  }

  vector<int> enum_moves() const {
    vector<int> result;
    for (auto kv : orig_locs)
      if (is_center(kv.second)) {
        result.push_back(kv.first);
        result.push_back(kv.first | VERT);
        result.push_back(kv.first - 1);
        result.push_back((kv.first - 10) | VERT);
      }
    return result;
  }

  void instantiate(vector<PatternInstance> &output) const {
    for (int i = 1 - i1; i < n - 1 - i2; i++)
      for (int j = 1 - j1; j < n - 1 - j2; j++) {
        PatternInstance pi;
        int q = 0;
        for (auto kv : orig_locs)
          if (is_center(kv.second))
            pi.idxs[q++] = (kv.first / 10 + i) * n + kv.first % 10 + j;
        assert(q == 4);
        for (int mv : moves) {
          int idx = mv & ~VERT;
          idx = (idx / 10 + i) * n + idx % 10 + j;
          if (mv & VERT)
            idx |= VERT;
          pi.moves.push_back(idx);
        }
        output.push_back(pi);
      }
  }
};


struct PatternGenerator {
  vector<Pattern> result;
  set<map<int, int> > used;

  void rec(Pattern p, int depth) {
    if (depth == 0) {
      if (used.count(p.orig_locs) == 0) {
        used.insert(p.orig_locs);
        result.push_back(p);
      }
      return;
    }

    for (int mv : p.enum_moves()) {
      Pattern p2 = p;
      if (p2.make_move(mv))
        rec(p2, depth - 1);
    }
  }

  void generate(int depth) {
    Pattern start;
    start.orig_locs[44] = 44;
    start.orig_locs[45] = 45;
    start.orig_locs[54] = 54;
    start.orig_locs[55] = 55;
    start.i1 = start.j1 = 4;
    start.i2 = start.j2 = 6;

    // to eliminate equivalent shorter patterns
    for (int i = 0; i < depth; i++)
      rec(start, i);
    result.clear();

    rec(start, depth);
  }
};


std::ostream& operator<<(std::ostream &out, const Pattern &p) {
  for (int i = p.i1; i < p.i2; i++) {
    for (int j = p.j1; j < p.j2; j++) {
      int idx = 10 * i + j;
      if (p.orig_locs.count(idx)) {
        if (p.is_center(p.orig_locs.at(idx)))
          out << "*  ";
        else
          out << ".  ";
        //out << p.orig_locs.at(idx) << " ";
      } else
        out << "   ";
    }
    out << endl;
  }
  out << "moves: ";
  for (int m : p.moves) {
    if (m & VERT)
      out << (m &~ VERT) << "v ";
    else
      out << m << "h ";
  }
  out << endl;
  return out;
}


