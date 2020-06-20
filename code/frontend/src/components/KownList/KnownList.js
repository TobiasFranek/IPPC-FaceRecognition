import React, { useState } from 'react';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import fromUnixTime from 'date-fns/fromUnixTime';
import format from 'date-fns/format';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import Divider from '@material-ui/core/Divider';
import InboxIcon from '@material-ui/icons/Inbox';
import DraftsIcon from '@material-ui/icons/Drafts';
import DeleteIcon from '@material-ui/icons/Delete';
import CreateIcon from '@material-ui/icons/Create';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import facesAPI from '../../api/faces';

export default ({ faces, onFacesChange }) => {

  const deleteFace = (id) => {
    facesAPI.deleteFace(id).then(() => {
      if (onFacesChange) {
        onFacesChange(faces.filter((face) => face.id !== id));
      }
    });
  }

  return (
    <>
      <TableContainer component={Paper}>
        <Table aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Image</TableCell>
              <TableCell align="center">Name</TableCell>
              <TableCell align="center">Visits</TableCell>
              <TableCell align="center">Last Seen</TableCell>
              <TableCell align="center"></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {faces.map((face) => (
              <TableRow key={face.id}>
                <TableCell component="th" scope="row">
                  <img src={face.image} />
                </TableCell>
                <TableCell align="center">{face.name}</TableCell>
                <TableCell align="center">{face.counter}</TableCell>
                <TableCell align="center">{format(fromUnixTime(face.last_seen), 'yyyy.dd.MM HH:mm:ss')}</TableCell>
                <TableCell align="center">
                  <List component="nav">
                    <ListItem button onClick={() => deleteFace(face.id)}>
                      <ListItemIcon>
                        <DeleteIcon />
                      </ListItemIcon>
                      <ListItemText primary="Delete" />
                    </ListItem>
                  </List>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  )
}