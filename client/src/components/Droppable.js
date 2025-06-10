import React from 'react';
import {useDroppable} from '@dnd-kit/core';

function Droppable(props) {
  const {setNodeRef} = useDroppable({
    id: props.id, // Use the id prop passed from parent
  });
  
  return (
    <div ref={setNodeRef}>
      {props.children}
    </div>
  );
}

export default Droppable;