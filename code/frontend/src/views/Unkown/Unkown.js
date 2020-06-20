import React, { useEffect, useState } from 'react';
import faceAPI from '../../api/faces';
import { Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import UnkownList from '../../components/UnkownList/UnkownList';

const useStyles = makeStyles((theme) => ({
  toolbar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'flex-end',
    padding: theme.spacing(0, 1),
    // necessary for content to be below app bar
    ...theme.mixins.toolbar,
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3),
  }
}));


export default () => {
  const classes = useStyles();
  const [faces, setFaces] = useState();

  useEffect(() => {
    faceAPI.getUnkown().then((response) => {
      setFaces(response.data);
    });
  }, []);

  const onFacesChange = (faces) => {
    setFaces(faces);
  }

  return (
    <main className={classes.content}>
      <div className={classes.toolbar} />
      <Typography variant="h3" component="h2">
        Unkown Faces
      </Typography>

      {faces
        ? (
          <UnkownList 
            onFacesChange={onFacesChange}
            faces={faces} 
          />
        )
        : null}
    </main>
  )
}