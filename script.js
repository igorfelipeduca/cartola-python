// script.js — MongoDB Shell Script (mongosh)
// Execute com: mongosh <connection-string> < script.js
// Ou copie e cole no shell interativo do MongoDB

// Use o banco de dados
use("futebol_app");

// Drop collections if they exist
db.time_usuario_jogador.drop();
db.time_usuario.drop();
db.jogador.drop();
db.time_oficial.drop();
db.usuario.drop();

// Create collections
db.createCollection("usuario");
db.createCollection("time_oficial");
db.createCollection("jogador");
db.createCollection("time_usuario");
db.createCollection("time_usuario_jogador");

// Create indexes for unique constraints
db.usuario.createIndex({ "email": 1 }, { unique: true });
db.time_oficial.createIndex({ "sigla": 1 }, { unique: true });
db.time_usuario_jogador.createIndex({ "time_usuario_id": 1, "jogador_id": 1 }, { unique: true });

// Insert sample data
db.usuario.insertMany([
  {
    _id: 1,
    nome: "Eduardo Fontes",
    email: "edu@example.com",
    senha: "hash_senha",
    sexo: "M",
    telefone: "77-99122-9637",
    data_nascimento: "2000-08-25",
    time_preferido: "FURIA"
  },
  {
    _id: 2,
    nome: "Larissa",
    email: "lari@example.com",
    senha: "hash",
    sexo: "F",
    telefone: null,
    data_nascimento: "2001-03-10",
    time_preferido: "LOUD"
  }
]);

db.time_oficial.insertMany([
  { _id: 1, nome: "Furia Esports", sigla: "FUR", nome_curto: "FURIA" },
  { _id: 2, nome: "LOUD", sigla: "LOD", nome_curto: "LOUD" }
]);

db.jogador.insertMany([
  { _id: 1, nome: "Jogador A", posicao: "Atacante", time_id: 1 },
  { _id: 2, nome: "Jogador B", posicao: "Meio-campo", time_id: 1 },
  { _id: 3, nome: "Jogador C", posicao: "Defensor", time_id: 2 },
  { _id: 4, nome: "Jogador D", posicao: "Goleiro", time_id: null }
]);

db.time_usuario.insertMany([
  { _id: 1, nome: "Time do Edu", usuario_id: 1 },
  { _id: 2, nome: "Time da Lari", usuario_id: 2 }
]);

db.time_usuario_jogador.insertMany([
  { _id: 1, time_usuario_id: 1, jogador_id: 1 },
  { _id: 2, time_usuario_id: 1, jogador_id: 2 },
  { _id: 3, time_usuario_id: 1, jogador_id: 4 },
  { _id: 4, time_usuario_id: 2, jogador_id: 2 },
  { _id: 5, time_usuario_id: 2, jogador_id: 3 }
]);

print("\n✓ Collections criadas e dados inseridos com sucesso!\n");

// CONSULTAS (Q1–Q5)

print("=".repeat(80));
print("Q1: Listar todos os jogadores com seus times oficiais");
print("=".repeat(80));
db.jogador.aggregate([
  {
    $lookup: {
      from: "time_oficial",
      localField: "time_id",
      foreignField: "_id",
      as: "time"
    }
  },
  {
    $unwind: {
      path: "$time",
      preserveNullAndEmptyArrays: true
    }
  },
  {
    $project: {
      id: "$_id",
      nome: 1,
      posicao: 1,
      time_oficial: { $ifNull: ["$time.nome", null] }
    }
  },
  {
    $sort: { time_oficial: 1, nome: 1 }
  }
]).forEach(printjson);

print("\n" + "=".repeat(80));
print("Q2: Listar times de usuários com seus jogadores");
print("=".repeat(80));
db.time_usuario.aggregate([
  {
    $lookup: {
      from: "usuario",
      localField: "usuario_id",
      foreignField: "_id",
      as: "usuario"
    }
  },
  { $unwind: "$usuario" },
  {
    $lookup: {
      from: "time_usuario_jogador",
      localField: "_id",
      foreignField: "time_usuario_id",
      as: "jogadores_rel"
    }
  },
  { $unwind: "$jogadores_rel" },
  {
    $lookup: {
      from: "jogador",
      localField: "jogadores_rel.jogador_id",
      foreignField: "_id",
      as: "jogador"
    }
  },
  { $unwind: "$jogador" },
  {
    $project: {
      time_usuario: "$nome",
      dono: "$usuario.nome",
      jogador: "$jogador.nome",
      posicao: "$jogador.posicao"
    }
  },
  {
    $sort: { time_usuario: 1, jogador: 1 }
  }
]).forEach(printjson);

print("\n" + "=".repeat(80));
print("Q3: Contar jogadores por posição em cada time oficial");
print("=".repeat(80));
db.jogador.aggregate([
  {
    $match: { time_id: { $ne: null } }
  },
  {
    $lookup: {
      from: "time_oficial",
      localField: "time_id",
      foreignField: "_id",
      as: "time"
    }
  },
  { $unwind: "$time" },
  {
    $group: {
      _id: {
        time_oficial: "$time.nome",
        posicao: "$posicao"
      },
      qtd: { $sum: 1 }
    }
  },
  {
    $project: {
      time_oficial: "$_id.time_oficial",
      posicao: "$_id.posicao",
      qtd: 1
    }
  },
  {
    $sort: { time_oficial: 1, qtd: -1 }
  }
]).forEach(printjson);

print("\n" + "=".repeat(80));
print("Q4: Listar jogadores sem time oficial");
print("=".repeat(80));
db.jogador.find(
  { time_id: null },
  { _id: 1, nome: 1, posicao: 1 }
).forEach(printjson);

print("\n" + "=".repeat(80));
print("Q5: Para um usuário específico, quantos jogadores do elenco dele");
print("    pertencem ao seu 'time preferido'");
print("=".repeat(80));
db.usuario.aggregate([
  {
    $lookup: {
      from: "time_usuario",
      localField: "_id",
      foreignField: "usuario_id",
      as: "times"
    }
  },
  { $unwind: "$times" },
  {
    $lookup: {
      from: "time_usuario_jogador",
      localField: "times._id",
      foreignField: "time_usuario_id",
      as: "jogadores_rel"
    }
  },
  { $unwind: "$jogadores_rel" },
  {
    $lookup: {
      from: "jogador",
      localField: "jogadores_rel.jogador_id",
      foreignField: "_id",
      as: "jogador"
    }
  },
  { $unwind: "$jogador" },
  {
    $lookup: {
      from: "time_oficial",
      localField: "jogador.time_id",
      foreignField: "_id",
      as: "time_oficial"
    }
  },
  { $unwind: "$time_oficial" },
  {
    $lookup: {
      from: "time_oficial",
      localField: "time_preferido",
      foreignField: "nome_curto",
      as: "time_preferido_obj"
    }
  },
  {
    $unwind: {
      path: "$time_preferido_obj",
      preserveNullAndEmptyArrays: true
    }
  },
  {
    $match: {
      $expr: { $eq: ["$time_oficial.sigla", "$time_preferido_obj.sigla"] }
    }
  },
  {
    $group: {
      _id: {
        usuario: "$nome",
        time_preferido: "$time_preferido"
      },
      jogadores_do_time_preferido: { $sum: 1 }
    }
  },
  {
    $project: {
      usuario: "$_id.usuario",
      time_preferido: "$_id.time_preferido",
      jogadores_do_time_preferido: 1
    }
  }
]).forEach(printjson);

print("\n✓ Script executado com sucesso!");
