import React, { useEffect, useState } from "react";
import "../styles.css";
import axios from "axios";
import {
  DragDropContext,
  Droppable,
  Draggable,
} from "@hello-pangea/dnd";
const API = "https://trello-clone-7ek1.onrender.com";
function Board() {
  const [lists, setLists] = useState([]);
  const [boards, setBoards] = useState([]);
  const [boardId, setBoardId] = useState(null);
  const [cards, setCards] = useState({});
  const [search, setSearch] = useState("");
  const [filterLabel, setFilterLabel] = useState("");
  const [filterMember, setFilterMember] = useState("");
  const [filterDue, setFilterDue] = useState("");

  const fetchBoards = async () => {
    const res = await axios.get(`${API}/boards`);
    setBoards(res.data);
  
    if (res.data.length > 0) {
      setBoardId(res.data[0].id); // default board
    }
  };

    if (boardId) {
    fetchLists();
  }
}, [boardId]);useEffect(() => {
    fetchBoards();
  }, []);
  
  useEffect(() => {
    if (boardId) {
      fetchLists();
    }
  }, [boardId]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchLists = async () => {
    const res = await axios.get(
      `${API}/lists/${boardId}`
    );
    setLists(res.data);
    res.data.forEach((list) => fetchCards(list.id));
  };

  // ✅ UPDATED (IMPORTANT)
  const fetchCards = async (listId) => {
    const res = await axios.get(
      `${API}/cards/${listId}`
    );

    const updated = res.data.map((card) => ({
      ...card,
      labels: card.labels || [],
      checklist: card.checklist || [],
      members: card.members || [],
    }));

    setCards((prev) => ({ ...prev, [listId]: updated }));
  };

  // ================= LIST =================

  const addList = async () => {
    const title = prompt("List name:");
    if (!title) return;
    await axios.post(`${API}/lists`, null, {
      params: { title, board_id: boardId },
    });
    fetchLists();
  };

  const editList = async (id) => {
    const title = prompt("New title:");
    if (!title) return;
    await axios.put(
      `${API}/lists/${id}?title=${title}`
    );
    fetchLists();
  };

  const deleteList = async (id) => {
    await axios.delete(`${API}/lists/${id}`);
    fetchLists();
  };

  // ================= CARD =================

  const addCard = async (listId) => {
    const title = prompt("Card title:");
    if (!title) return;

    await axios.post(
      `${API}/cards?title=${title}&list_id=${listId}`
    );

    fetchLists();
  };

  const editCard = async (cardId) => {
    const title = prompt("New title:");
    const description = prompt("Description:");
    if (!title) return;

    await axios.put(
      `${API}/cards/${cardId}?title=${title}&description=${description}`
    );

    fetchLists();
  };

  const deleteCard = async (cardId) => {
    await axios.put(
      `${API}/cards/${cardId}/archive`
    );
    fetchLists();
  };
  const handleSearch = async () => {
    if (!search) {
      fetchLists();
      return;
    }
  
    const res = await axios.get(
      `${API}/cards/search/${boardId}?query=${search}`
    );
  
    const grouped = {};
    lists.forEach((list) => {
      grouped[list.id] = [];
    });
    res.data.forEach((card) => {
      if (grouped[card.list_id]) {
        grouped[card.list_id].push(card);
      }
    });
      
  
    setCards(grouped);
  };
  const handleFilter = async () => {
    const res = await axios.get(
      `${API}/cards/filter/${boardId}?label=${filterLabel}&member=${filterMember}&due=${filterDue}`
    );
  
    const grouped = {};
    lists.forEach((list) => {
      grouped[list.id] = [];
    });
    res.data.forEach((card) => {
      if (grouped[card.list_id]) {
        grouped[card.list_id].push(card);
      }
    });
  
    setCards(grouped);
  };

  // ================= DRAG =================

  const onDragEnd = async (result) => {
    const { source, destination, type } = result;
    if (!destination) return;

    if (type === "list") {
      const newLists = Array.from(lists);
      const [moved] = newLists.splice(source.index, 1);
      newLists.splice(destination.index, 0, moved);

      setLists(newLists);

      const order = newLists.map((l) => Number(l.id));

      await axios.put(`${API}/lists/reorder`, {
        order,
      });

      return;
    }

    const sourceListId = parseInt(source.droppableId);
    const destListId = parseInt(destination.droppableId);

    const sourceCards = Array.from(cards[sourceListId] || []);
    const destCards =
      sourceListId === destListId
        ? sourceCards
        : Array.from(cards[destListId] || []);

    const [movedCard] = sourceCards.splice(source.index, 1);

    if (sourceListId === destListId) {
      sourceCards.splice(destination.index, 0, movedCard);

      setCards({
        ...cards,
        [sourceListId]: sourceCards,
      });

      const order = sourceCards.map((c) => Number(c.id));

      await axios.put(`${API}/cards/reorder`, {
        order,
      });
    } else {
      movedCard.list_id = destListId;
      destCards.splice(destination.index, 0, movedCard);

      setCards({
        ...cards,
        [sourceListId]: sourceCards,
        [destListId]: destCards,
      });

      await axios.put(
        `${API}/cards/${movedCard.id}/move?new_list_id=${destListId}`
      );
    }
  };
  const handleUpload = async (cardId, file) => {
    if (!file) return;
  
    const formData = new FormData();
    formData.append("file", file);
  
    await axios.post(
      `${API}/cards/${cardId}/upload`,
      formData
    );
  
    fetchLists(); // refresh
  };

  // ================= UI =================

  return (
    <div
  className="container"
  style={{
    background:
      boards.find((b) => b.id === boardId)?.background || "#0079bf",
    minHeight: "100vh",
  }}
>
      <div className="controls">
      <input
  type="color"
  onChange={async (e) => {
    const color = e.target.value;

    await axios.put(
      `${API}/boards/${boardId}/background?background=${color}`
    );

    fetchBoards();
  }}
/>
      <select
  value={boardId || ""}
  onChange={(e) => setBoardId(e.target.value)}
>
  {boards.map((b) => (
    <option key={b.id} value={b.id}>
      {b.title}
    </option>
  ))}
</select>


<button
  onClick={async () => {
    const title = prompt("Board name:");
    if (!title) return;

    await axios.post(`${API}/boards`, null, {
      params: { title },
    });

    fetchBoards();
  }}
>
  + Add Board
</button>
  {/* 🔍 SEARCH */}
  <input
    placeholder="Search cards..."
    value={search}
    onChange={(e) => setSearch(e.target.value)}
  />
  <button onClick={handleSearch}>Search</button>

  {/* 🎯 FILTER */}
  <input
    placeholder="Label"
    onChange={(e) => setFilterLabel(e.target.value)}
  />
  <input
    placeholder="Member"
    onChange={(e) => setFilterMember(e.target.value)}
  />
  <input
    placeholder="Due date (YYYY-MM-DD)"
    onChange={(e) => setFilterDue(e.target.value)}
  />
  <button onClick={handleFilter}>Filter</button>

  <button onClick={fetchLists}>Reset</button>
</div>
<h2>
  {boards.find((b) => b.id === boardId)?.title}
</h2>
      <button onClick={addList}>+ Add List</button>

      <DragDropContext onDragEnd={onDragEnd}>
        <Droppable droppableId="lists" direction="horizontal" type="list">
          {(provided) => (
            <div
              ref={provided.innerRef}
              {...provided.droppableProps}
              className="board"
            >
              {lists.map((list, index) => (
                <Draggable
                  key={list.id}
                  draggableId={`list-${list.id}`}
                  index={index}
                >
                  {(provided) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      className="list"
style={{
  minHeight: "300px",
  ...provided.draggableProps.style,
}}
                    >
                      <div {...provided.dragHandleProps}>
                        <h3>{list.title}</h3>
                      </div>

                      <button onClick={() => editList(list.id)}>Edit</button>
                      <button onClick={() => deleteList(list.id)}>Delete</button>

                      <button onClick={() => addCard(list.id)}>
                        + Add Card
                      </button>

                      <Droppable droppableId={String(list.id)} type="card">
                        {(provided) => (
                          <div
                            ref={provided.innerRef}
                            {...provided.droppableProps}
                            className="card-container"
                            style={{minHeight: "150px"}}
                          >
                            {(cards[list.id] || []).map((card, i) => (
                              <Draggable
                                key={card.id}
                                draggableId={`card-${card.id}`}
                                index={i}
                              >
                                {(provided) => (
                                  <div
                                    ref={provided.innerRef}
                                    {...provided.draggableProps}
                                    {...provided.dragHandleProps}
                                    onMouseDown={(e) => e.stopPropagation()}
                                    className="card"
style={{
  ...provided.draggableProps.style,
}}
                                  >
                                    {card.cover_image && (
  <img
    src={`${API}/${card.cover_image}`}
    alt="cover"
    style={{
      width: "100%",
      height: "120px",
      objectFit: "cover",
      borderRadius: "6px",
      marginBottom: "5px",
    }}
  />
)}
                                    <b>{card.title}</b>
                                    <input
  placeholder="Write a comment..."
  style={{
    width: "100%",
    marginTop: "5px",
    padding: "5px",
    borderRadius: "5px",
    border: "1px solid #ccc",
    fontSize: "12px"
  }}
  onKeyDown={async (e) => {
    if (e.key === "Enter") {
      if (!e.target.value) return;

      await axios.post(
        `${API}/cards/${card.id}/comments?text=${e.target.value}`
      );

      e.target.value = "";
      fetchLists();
    }
  }}
/>
{/* 📜 COMMENTS */}
<div style={{ marginTop: "5px" }}>
  {card.comments?.map((c) => (
    <div
      key={c.id}
      style={{
        background: "#f4f5f7",
        padding: "5px",
        borderRadius: "5px",
        marginTop: "3px",
        fontSize: "12px"
      }}
    >
      💬 {c.text}
    </div>
  ))}
</div>
{/* 📊 ACTIVITY */}
<div style={{ marginTop: "5px", fontSize: "11px", color: "gray" }}>
  <b>Activity</b>
  {card.activity?.map((a) => (
    <div key={a.id}>📌 {a.action}</div>
  ))}
</div>

                                    {card.cover_image && (
  <button
    style={{
      fontSize: "10px",
      marginTop: "5px",
      background: "red",
      color: "white",
      border: "none",
      borderRadius: "3px",
      padding: "2px 5px",
    }}
    onClick={async () => {
      await axios.put(
        `${API}/cards/${card.id}/cover?file_path=`
      );
      fetchLists();
    }}
  >
    Remove Cover
  </button>
)}
                                    <input
  type="file"
  onChange={(e) => handleUpload(card.id, e.target.files[0])}
/>
{card.attachments &&
  card.attachments.map((a) => (
    <div key={a.id} style={{ marginTop: "5px" }}>

      {/* 🔥 SHOW IMAGE IF IMAGE */}
      {a.file_name.match(/\.(jpg|jpeg|png|webp)$/i) && (
        <img
          src={`${API}/${a.file_path}`}
          alt="attachment"
          style={{
            width: "100%",
            height: "80px",
            objectFit: "cover",
            borderRadius: "5px",
          }}
        />
      )}

      {/* FILE NAME */}
      <div style={{ fontSize: "12px" }}>
        📎 {a.file_name}
      </div>

      {/* SET COVER */}
      {a.file_name.match(/\.(jpg|jpeg|png|webp)$/i) && (
        <button
          style={{ fontSize: "10px", marginTop: "2px" }}
          onClick={async () => {
            await axios.put(
              `${API}/cards/${card.id}/cover?file_path=${a.file_path}`
            );
            fetchLists();
          }}
        >
          Set Cover
        </button>
      )}
    </div>
))}

                                    {/* LABELS */}
                                    <div style={{ display: "flex", gap: "5px", flexWrap: "wrap" }}>
                                      {card.labels?.map((label) => (
                                        <span
                                          key={label.id}
                                          onClick={async () => {
                                            await axios.delete(
                                              `${API}/labels/${label.id}`
                                            );
                                            fetchLists();
                                          }}
                                          style={{
                                            background: label.color || "gray",
                                            color: "white",
                                            padding: "2px 6px",
                                            borderRadius: "4px",
                                            fontSize: "12px",
                                            cursor: "pointer",
                                          }}
                                        >
                                          {label.name} ❌
                                        </span>
                                      ))}
                                    </div>

                                    {/* MEMBERS */}
                                    <div style={{ fontSize: "12px", color: "gray" }}>
                                      👤 {card.members?.map((m) => m.name).join(", ")}
                                    </div>

                                    {/* DUE DATE */}
                                    {card.due_date && (
                                      <div style={{ color: "red", fontSize: "12px" }}>
                                        ⏰ {card.due_date}
                                      </div>
                                    )}

                                    {/* CHECKLIST */}
                                    <div>
                                      {card.checklist?.map((item) => (
                                        <div key={item.id}>
                                          <input
                                            type="checkbox"
                                            checked={item.completed}
                                            onChange={async () => {
                                              await axios.put(
                                                `${API}/checklist/${item.id}`
                                              );
                                              fetchLists();
                                            }}
                                          />
                                          {item.text}
                                        </div>
                                      ))}
                                    </div>

                                    <p>{card.description}</p>
                                    {/* 💬 COMMENTS */}



                                    <button onClick={() => editCard(card.id)}>
                                      Edit
                                    </button>

                                    <button onClick={() => deleteCard(card.id)}>
                                      Delete
                                    </button>

                                    {/* ADD LABEL */}
                                    <button
                                      onClick={async () => {
                                        const name = prompt("Label name:");
                                        const color = prompt("Color (red/green/blue)");
                                        if (!name || !color) return;

                                        await axios.post(
                                          `${API}/cards/${card.id}/labels?name=${name}&color=${color}`
                                        );
                                        fetchLists();
                                      }}
                                    >
                                      + Label
                                    </button>

                                    {/* ADD CHECKLIST */}
                                    <button
                                      onClick={async () => {
                                        const text = prompt("Checklist item:");
                                        await axios.post(
                                          `${API}/cards/${card.id}/checklist?text=${text}`
                                        );
                                        fetchLists();
                                      }}
                                    >
                                      + Checklist
                                    </button>

                                    {/* ADD MEMBER */}
                                    <button
                                      onClick={async () => {
                                        const name = prompt("Member name:");
                                        await axios.post(
                                          `${API}/cards/${card.id}/members?name=${name}`
                                        );
                                        fetchLists();
                                      }}
                                    >
                                      + Member
                                    </button>

                                    {/* ADD DUE DATE */}
                                    <button
                                      onClick={async () => {
                                        const date = prompt("YYYY-MM-DD");
                                        await axios.put(
                                          `${API}/cards/${card.id}/due?due_date=${date}`
                                        );
                                        fetchLists();
                                      }}
                                    >
                                      + Due Date
                                    </button>
                                  </div>
                                )}
                              </Draggable>
                            ))}
                            {provided.placeholder}
                          </div>
                        )}
                      </Droppable>
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>
    </div>
  );
}

export default Board;
